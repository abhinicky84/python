# Product Color Variants (Adobe Firefly)

Generate a color-variant product image using Adobe Firefly image generation with a reference image and hex color prompt.

## What it does
- Sends the product image as a reference to Adobe Firefly
- Uses a prompt template to recolor the product to the requested hex
- Saves the AI-generated image returned by Firefly

## Setup
1. Copy `.env.example` to `.env` and fill in Firefly credentials:
   - `FIREFLY_API_ENDPOINT`
   - `FIREFLY_API_KEY`
   - `FIREFLY_ACCESS_TOKEN`
2. Build with Maven.

```bash
mvn -f Azure/product-color-variants/pom.xml -DskipTests package
```

## Run
```bash
java -jar Azure/product-color-variants/target/product-color-variants-1.0.0.jar \
  --image path/to/product.jpg \
  --hex #2a8fdb \
  --output output
```

## Outputs
- `output/generated.png` - Firefly-generated color variant
- `output/firefly_response.json` - raw response JSON when returned

## Notes
- Firefly APIs require OAuth access tokens. Make sure `FIREFLY_ACCESS_TOKEN` is valid.
- This implementation sends a multipart request with a reference image and prompt. If your Firefly endpoint expects a different payload, update `FireflyClient`.
- AI generation may introduce small variation versus the original product photo.
