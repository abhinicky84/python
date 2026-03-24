package com.retail.colorvariants;

import java.nio.file.Path;
import java.util.Map;

public final class Settings {
    public final String fireflyEndpoint;
    public final String fireflyApiKey;
    public final String fireflyAccessToken;
    public final String promptTemplate;
    public final int numImages;
    public final int timeoutSeconds;

    private Settings(
            String fireflyEndpoint,
            String fireflyApiKey,
            String fireflyAccessToken,
            String promptTemplate,
            int numImages,
            int timeoutSeconds
    ) {
        this.fireflyEndpoint = fireflyEndpoint;
        this.fireflyApiKey = fireflyApiKey;
        this.fireflyAccessToken = fireflyAccessToken;
        this.promptTemplate = promptTemplate;
        this.numImages = numImages;
        this.timeoutSeconds = timeoutSeconds;
    }

    public static Settings load(Path dotenvPath) {
        Map<String, String> envFile = Dotenv.load(dotenvPath);

        String endpoint = value("FIREFLY_API_ENDPOINT", envFile).replaceAll("/+$", "");
        String apiKey = value("FIREFLY_API_KEY", envFile).trim();
        String accessToken = value("FIREFLY_ACCESS_TOKEN", envFile).trim();
        String promptTemplate = valueOr(
                "FIREFLY_PROMPT_TEMPLATE",
                envFile,
                "Recolor the product to the exact hex color {hex}. Keep the product shape, lighting, and background unchanged."
        );

        int numImages = parseInt(valueOr("FIREFLY_NUM_IMAGES", envFile, "1"), 1);
        int timeoutSeconds = parseInt(valueOr("FIREFLY_TIMEOUT_SECONDS", envFile, "120"), 120);

        return new Settings(endpoint, apiKey, accessToken, promptTemplate, numImages, timeoutSeconds);
    }

    private static String value(String key, Map<String, String> envFile) {
        String fromEnv = System.getenv(key);
        if (fromEnv != null && !fromEnv.isBlank()) {
            return fromEnv.trim();
        }
        String fromFile = envFile.get(key);
        return fromFile == null ? "" : fromFile.trim();
    }

    private static String valueOr(String key, Map<String, String> envFile, String fallback) {
        String value = value(key, envFile);
        return value.isBlank() ? fallback : value;
    }

    private static int parseInt(String value, int fallback) {
        try {
            return Integer.parseInt(value.trim());
        } catch (Exception ignored) {
            return fallback;
        }
    }
}
