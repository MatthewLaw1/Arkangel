# Focus Monitor

A Python-based focus monitoring tool that uses Claude to analyze your screen activity and determine if you're staying on task.

## Features
- Takes periodic screenshots of your work environment
- Uses Claude AI to analyze screen content
- Intelligently determines if you're focused on your stated task
- Considers main content vs active distractions with 80/20 weighting
- Ignores non-disruptive elements like inactive tabs or UI elements

## Requirements
- Python 3.11 or higher
- An Anthropic API key (for Claude)
- macOS (currently tested on macOS, may work on other platforms)

## Setup

1. Clone the repository:
```bash
git clone [your-repo-url]
cd [repo-name]
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install anthropic mss python-dotenv Pillow
```

4. Create a `.env` file in the project root:
```bash
echo "ANTHROPIC_API_KEY=your-api-key-here" > .env
```
Replace `your-api-key-here` with your actual Anthropic API key.

## Usage

1. Edit your current task in `main.py`:
```python
CURRENT_TASK = "Working on a math project - solving calculus problems"
```
Change this to match what you're working on.

2. Run the monitor:
```bash
python main.py
```

3. The program will:
   - Take screenshots every 2 seconds
   - Analyze them using Claude
   - Print whether you're focused or distracted
   - Show what content is on screen and any active distractions

4. Press Ctrl+C to stop monitoring.

## How It Works

The tool uses a sophisticated analysis system:
- Main Content (80% weight): What dominates your screen
- Active Distractions (20% weight): Things actively competing for attention

Something is only counted as a distraction if it's:
- Actively playing (video/audio)
- Taking up significant screen space
- Clearly engaging attention (e.g., open chat with new messages)

UI elements, inactive tabs, and small windows are NOT counted as distractions.

## Example Output
```
Starting distraction monitor for task: Working on a math project
Press Ctrl+C to stop...

Claude's Analysis:
FOCUSED: yes
MAIN CONTENT: Math equations and graphs visible on screen
ACTIVE DISTRACTIONS: none
REASONING: Screen dominated by calculus content with no major competing elements.
```

## Privacy Note
Screenshots are saved temporarily in the `screenshots` directory and are overwritten each time you run the program. They are only used for Claude's analysis and are not stored permanently or sent anywhere except to Claude's API for analysis.

## Customization
You can modify:
- Screenshot interval (default: 2 seconds)
- Task description
- Analysis weights
- What counts as a distraction

Edit these in `main.py` as needed.

## Troubleshooting

If you see "No module named 'xxx'":
```bash
pip install xxx
```

If screenshots aren't capturing properly:
- Ensure you have screen recording permissions enabled for your terminal/IDE
- Try running the program with elevated privileges

## Contributing
Feel free to open issues or submit pull requests!
