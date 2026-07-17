# House Interior Generator

A Streamlit app: pick door material/color, wall texture/color, design style,
flooring, and lighting from dropdowns → get an AI-generated realistic preview
of the room.

## Setup (local)

```bash
pip install -r requirements.txt
export HF_API_TOKEN="hf_your-token-here"
streamlit run app.py
```

## Setup (Streamlit Community Cloud)

1. Push this folder to a GitHub repo.
2. Go to https://share.streamlit.io and deploy the repo, main file `app.py`.
3. In the app's **Settings → Secrets**, add:
   ```toml
   HF_API_TOKEN = "hf_your-token-here"
   ```
4. Deploy. Done.

## Notes / things you may want to change

- **Model**: uses Hugging Face's Inference Providers with `stabilityai/stable-diffusion-xl-base-1.0`
  (set in `HF_MODEL` near the top of `app.py`). Swap in any other text-to-image
  model repo id on Hugging Face if you want a different look, speed, or cost.
- **Why `huggingface_hub` instead of raw HTTP**: Hugging Face retired the old
  `api-inference.huggingface.co` URL in favor of a newer routing system
  (`router.huggingface.co`, picked per-model/provider). The official
  `huggingface_hub` client always talks to the current routing endpoint, so
  the app won't break again the next time Hugging Face changes the URL.
- **If a model gives an error**: some models require billing/credits set up
  on your Hugging Face account for the provider that serves them, or aren't
  available through Inference Providers at all. If `stable-diffusion-xl-base-1.0`
  errors out, try `stabilityai/stable-diffusion-2-1` or check the model's page
  on huggingface.co for an "Inference Providers" badge before using it.
- **Theme**: `.streamlit/config.toml` pins a light theme so text stays
  readable regardless of the viewer's OS/browser dark-mode setting.
- **Rooms/options**: all dropdown values live at the top of `app.py` in plain
  Python lists (`DOOR_MATERIALS`, `WALL_COLORS`, etc.) — add/remove options
  there, no other code changes needed.
- **Prompt**: `build_prompt()` is the single place that turns the form
  answers into the text prompt sent to the image model. Tweak wording there
  if generations don't match what you want.
- **Floor plan grounding**: right now the model only gets a text description
  (room type + finishes), not your actual floor plan image. If you want the
  generated room to match your exact floor plan's shape/window placement,
  the next step would be using an image-to-image / edit endpoint with your
  floor plan photo as input instead of pure text-to-image — happy to add
  that if you want it.
