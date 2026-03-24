package com.retail.colorvariants;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public final class Dotenv {
    private Dotenv() {
    }

    public static Map<String, String> load(Path path) {
        Map<String, String> values = new HashMap<>();
        if (path == null || !Files.exists(path)) {
            return values;
        }

        try {
            List<String> lines = Files.readAllLines(path);
            for (String line : lines) {
                String trimmed = line.trim();
                if (trimmed.isEmpty() || trimmed.startsWith("#")) {
                    continue;
                }
                int idx = trimmed.indexOf('=');
                if (idx <= 0) {
                    continue;
                }
                String key = trimmed.substring(0, idx).trim();
                String value = trimmed.substring(idx + 1).trim();
                values.put(key, value);
            }
        } catch (Exception ignored) {
            return values;
        }

        return values;
    }
}
