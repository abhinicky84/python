package com.retail.colorvariants;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

public final class Main {
    public static void main(String[] args) throws Exception {
        Arguments arguments = Arguments.parse(args);
        if (arguments == null) {
            Arguments.printUsage();
            System.exit(1);
            return;
        }

        Path projectRoot = Paths.get("").toAbsolutePath();
        Settings settings = Settings.load(projectRoot.resolve(".env"));

        FireflyClient client = new FireflyClient(settings);
        GeneratedImage generated = client.generateVariant(arguments.imagePath, arguments.hexColor);

        Path outputDir = arguments.outputDir;
        Files.createDirectories(outputDir);

        if (generated.rawResponse != null) {
            Path responsePath = outputDir.resolve("firefly_response.json");
            Files.writeString(responsePath, generated.rawResponse, StandardCharsets.UTF_8);
        }

        byte[] imageBytes = generated.imageBytes;
        if (imageBytes == null && generated.imageUrl != null) {
            imageBytes = client.downloadImage(generated.imageUrl);
        }

        if (imageBytes == null) {
            throw new IllegalStateException("Firefly response did not include image bytes or URL.");
        }

        Path outputImage = outputDir.resolve("generated.png");
        Files.write(outputImage, imageBytes);

        System.out.println("Generated image: " + outputImage);
        if (generated.imageUrl != null) {
            System.out.println("Image URL: " + generated.imageUrl);
        }
    }

    private static final class Arguments {
        final Path imagePath;
        final String hexColor;
        final Path outputDir;

        private Arguments(Path imagePath, String hexColor, Path outputDir) {
            this.imagePath = imagePath;
            this.hexColor = hexColor;
            this.outputDir = outputDir;
        }

        static Arguments parse(String[] args) {
            Path imagePath = null;
            String hex = null;
            Path output = Paths.get("output");

            for (int i = 0; i < args.length; i++) {
                switch (args[i]) {
                    case "--image" -> {
                        if (i + 1 < args.length) {
                            imagePath = Paths.get(args[++i]);
                        }
                    }
                    case "--hex" -> {
                        if (i + 1 < args.length) {
                            hex = args[++i];
                        }
                    }
                    case "--output" -> {
                        if (i + 1 < args.length) {
                            output = Paths.get(args[++i]);
                        }
                    }
                    default -> {
                    }
                }
            }

            if (imagePath == null || hex == null) {
                return null;
            }

            return new Arguments(imagePath, hex, output);
        }

        static void printUsage() {
            System.out.println("Usage: java -jar target/product-color-variants-1.0.0.jar --image <path> --hex <#RRGGBB> [--output <dir>]");
        }
    }
}
