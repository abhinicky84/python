package com.retail.colorvariants;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.Base64;
import java.util.UUID;

public final class FireflyClient {
    private final Settings settings;
    private final HttpClient httpClient;

    public FireflyClient(Settings settings) {
        this.settings = settings;
        this.httpClient = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(20))
                .build();
    }

    public GeneratedImage generateVariant(Path imagePath, String hex) throws Exception {
        if (settings.fireflyEndpoint.isBlank()) {
            throw new IllegalStateException("FIREFLY_API_ENDPOINT must be set.");
        }
        if (settings.fireflyApiKey.isBlank()) {
            throw new IllegalStateException("FIREFLY_API_KEY must be set.");
        }
        if (settings.fireflyAccessToken.isBlank()) {
            throw new IllegalStateException("FIREFLY_ACCESS_TOKEN must be set.");
        }

        byte[] imageBytes = Files.readAllBytes(imagePath);
        String prompt = settings.promptTemplate.replace("{hex}", hex);

        String boundary = "----firefly-boundary-" + UUID.randomUUID();
        byte[] payload = MultipartBodyBuilder.build(boundary)
                .addField("prompt", prompt)
                .addField("num_images", String.valueOf(settings.numImages))
                .addFile("reference_image", imagePath.getFileName().toString(), "image/jpeg", imageBytes)
                .toBytes();

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(settings.fireflyEndpoint))
                .timeout(Duration.ofSeconds(settings.timeoutSeconds))
                .header("Authorization", "Bearer " + settings.fireflyAccessToken)
                .header("x-api-key", settings.fireflyApiKey)
                .header("Content-Type", "multipart/form-data; boundary=" + boundary)
                .POST(HttpRequest.BodyPublishers.ofByteArray(payload))
                .build();

        HttpResponse<byte[]> response = httpClient.send(request, HttpResponse.BodyHandlers.ofByteArray());
        if (response.statusCode() != 200) {
            String body = new String(response.body(), StandardCharsets.UTF_8);
            if (body.length() > 400) {
                body = body.substring(0, 400);
            }
            throw new RuntimeException("Firefly request failed: " + response.statusCode() + " -> " + body);
        }

        String contentType = response.headers().firstValue("Content-Type").orElse("").toLowerCase();
        if (contentType.contains("image")) {
            return new GeneratedImage(response.body(), null, null);
        }

        if (contentType.contains("json")) {
            String json = new String(response.body(), StandardCharsets.UTF_8);
            GeneratedImage parsed = parseJsonResponse(json);
            return new GeneratedImage(parsed.imageBytes, parsed.imageUrl, json);
        }

        return new GeneratedImage(response.body(), null, null);
    }

    private GeneratedImage parseJsonResponse(String json) {
        JsonObject root = JsonParser.parseString(json).getAsJsonObject();
        JsonArray images = root.getAsJsonArray("images");
        if (images != null && images.size() > 0) {
            JsonObject first = images.get(0).getAsJsonObject();
            JsonElement url = first.get("url");
            if (url != null && url.isJsonPrimitive()) {
                return new GeneratedImage(null, url.getAsString(), json);
            }
            JsonElement base64 = first.get("image");
            if (base64 != null && base64.isJsonPrimitive()) {
                byte[] decoded = Base64.getDecoder().decode(base64.getAsString());
                return new GeneratedImage(decoded, null, json);
            }
        }
        return new GeneratedImage(null, null, json);
    }

    public byte[] downloadImage(String url) throws Exception {
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .timeout(Duration.ofSeconds(settings.timeoutSeconds))
                .GET()
                .build();
        HttpResponse<byte[]> response = httpClient.send(request, HttpResponse.BodyHandlers.ofByteArray());
        if (response.statusCode() != 200) {
            throw new RuntimeException("Failed to download generated image: " + response.statusCode());
        }
        return response.body();
    }

    private static final class MultipartBodyBuilder {
        private final String boundary;
        private final ByteArrayOutputBuffer buffer;

        private MultipartBodyBuilder(String boundary) {
            this.boundary = boundary;
            this.buffer = new ByteArrayOutputBuffer();
        }

        static MultipartBodyBuilder build(String boundary) {
            return new MultipartBodyBuilder(boundary);
        }

        MultipartBodyBuilder addField(String name, String value) {
            buffer.append("--" + boundary + "\r\n");
            buffer.append("Content-Disposition: form-data; name=\"" + name + "\"\r\n\r\n");
            buffer.append(value + "\r\n");
            return this;
        }

        MultipartBodyBuilder addFile(String name, String filename, String contentType, byte[] data) {
            buffer.append("--" + boundary + "\r\n");
            buffer.append("Content-Disposition: form-data; name=\"" + name + "\"; filename=\"" + filename + "\"\r\n");
            buffer.append("Content-Type: " + contentType + "\r\n\r\n");
            buffer.append(data);
            buffer.append("\r\n");
            return this;
        }

        byte[] toBytes() {
            buffer.append("--" + boundary + "--\r\n");
            return buffer.toByteArray();
        }
    }

    private static final class ByteArrayOutputBuffer {
        private byte[] data = new byte[0];

        void append(String text) {
            append(text.getBytes(StandardCharsets.UTF_8));
        }

        void append(byte[] bytes) {
            byte[] next = new byte[data.length + bytes.length];
            System.arraycopy(data, 0, next, 0, data.length);
            System.arraycopy(bytes, 0, next, data.length, bytes.length);
            data = next;
        }

        byte[] toByteArray() {
            return data;
        }
    }
}
