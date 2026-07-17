# House Interior Generator

A Streamlit app: pick door material/color, wall texture/color, design style,
flooring, and lighting from dropdowns → get an AI-generated realistic preview
of the room.

## Setup (local)

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="sk-your-key-here"
streamlit run app.py
```

## Setup (Streamlit Community Cloud)

1. Push this folder to a GitHub repo.
2. Go to https://share.streamlit.io and deploy the repo, main file `app.py`.
3. In the app's **Settings → Secrets**, add:
   ```toml
   OPENAI_API_KEY = "sk-your-key-here"
   ```
4. Deploy. Done.

## Notes / things you may want to change

- **Model**: uses `gpt-image-1` (OpenAI). Each image costs a small amount per
  call — check OpenAI's current image pricing before heavy use.
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
