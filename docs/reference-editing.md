# Editing with target and reference images

No training is required. The model receives both images each time you run the workflow.

1. Load `reference-edit-workflow.json` from the Workflows sidebar or file-open menu.
2. Find **Load Image** nodes. The first connects to `images.image_1` on **Text Encode Qwen Image 2.1**; it holds the target photo. The second connects to `images.image_2`; it holds the reference.
3. Upload a target and a clear reference photo you have permission to use. Similar face angles and lighting can make the reference less ambiguous.
4. Replace the example prompt. Use the exact reference tags `<image1>` and `<image2>` to assign roles. Name only the change you want, and say what should stay fixed.
5. Begin at resolution 512. Inspect faces and background details before increasing resolution or trying multiple operations.

Examples:

**Clothing reference**

> Edit `<image1>`. Replace only the jacket with the jacket shown in `<image2>`. Preserve the person’s face, hairstyle, expression, pose and the background of `<image1>`.

**Appearance reference**

> Edit `<image1>`. Use `<image2>` as the appearance reference for the same adult person. Change the sweater to navy blue. Preserve the person’s recognizable facial features, hairstyle, skin tone, expression, pose and the composition of `<image1>`.

The second image is guidance, not a face-lock guarantee. Check eyes, glasses, jewelry, proportions, hands and background. For a requested change of pose, Consistency may hold the old pose too strongly; compare the base workflow or reduce the adapter rather than assuming more adapters are better.

## Reuse without training

Save the workflow under a descriptive name such as **My reference edits**. Keep the reference file in local input storage and change only the target for later runs. The workflow stores prompts, references by filename, seed, settings and adapter choices. Back up the workflow and reference privately together; exporting the workflow JSON does not embed the original photo.

Do not place personal workflows in this Git repository's tracked `workflows/` folder. Use ComfyUI's ignored `.runtime/ComfyUI/user/default/workflows` storage. The model does not learn from these edits and retains no conversation memory between runs. Identity/style training through a LoRA is a separate project and has not been established on this tested Mac setup.

## Adapter choice

- **Consistency:** useful starting point for preserving untargeted regions; still reconstructs pixels.
- **Anything2Real:** intended for stylized-to-realistic human character transformations. Keep it off for routine photo recolors unless its effect is desired.
- **TheseAlpacas V2:** NSFW-labeled by its distributor, optional, not a required identity-preservation adapter.

Only use adapters compatible with Qwen Image **2.1**. Earlier 2511 adapters and models are not interchangeable with this pipeline.
