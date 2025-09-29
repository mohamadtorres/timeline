# Timeline MVP

A simple timeline/novel-writing tool for managing characters, places, and events, and visualizing them on a timeline.

## Features

- Add, edit, and delete **Characters**, **Places**, and **Events**
- Assign notes and images to each item
- Color support for characters
- Events connected to characters and places
- Timeline tab for viewing events chronologically

## Installation

1. Install [Python 3.9+](https://www.python.org/)  
2. Install requirements:

   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) Create a `pictures/` folder next to your code for images.

## Usage

Run the application:

```bash
python -m app.main
```

- Data is saved to `data/data.json`
- Images used in the app must be inside the `pictures/` folder

## Tabs

- **Characters:** Add/edit characters, pick color, add notes/images
- **Places:** Add/edit places, add notes/images
- **Events:** Add/edit events, link to characters/places, set dates, notes/images
- **Timeline:** See all events sorted by date

## License

MIT (or specify your license)