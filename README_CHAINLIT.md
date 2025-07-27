# Claude Web Runner - Chainlit Frontend

Welcome to Claude Web Runner! This is a web interface for interacting with Claude Code using a project-based organization system.

## ✨ Features

- **Project Management**: Create and organize your work into separate project folders
- **Thread Management**: Have multiple chat conversations within each project
- **Claude Code Integration**: All Claude operations happen in your selected project directories
- **File Viewing**: See the files and folders Claude creates in real-time
- **Session Persistence**: Your projects and threads are saved between sessions

## 🚀 Getting Started

### 1. Start the Backend API
First, make sure the Flask API server is running:
```bash
python app.py
```
The API should be available at http://localhost:5000

### 2. Start the Chainlit Frontend
In a new terminal, run:
```bash
chainlit run chainlit_app.py
```
The web interface will be available at http://localhost:8000

## 📋 How to Use

### Project Workflow
1. **Create or Select a Project** - This becomes your working directory
2. **Create or Select a Thread** - This is your chat conversation
3. **Chat with Claude** - All file operations happen in your project folder

### Navigation
- Use the **action buttons** to navigate between projects and threads
- In chat mode, type `/back` to return to thread selection
- Type `/files` to view your project's file structure
- Type `/help` for detailed help information

### Commands in Chat Mode
- `/back` - Return to thread selection
- `/files` - View project file tree
- `/help` - Show help information

## 🗂️ Project Structure

```
your-project/
├── <generated files by Claude>
├── <any folders Claude creates>
└── .threads/
    ├── threads.json      # Project metadata
    ├── thread-1.json     # Individual thread data
    └── thread-2.json     # Another thread
```

## 🔧 Technical Details

- **Frontend**: Chainlit (Python-based chat interface)
- **Backend**: Flask API with Claude CLI integration
- **Storage**: JSON files for project/thread metadata
- **Claude Sessions**: Each thread maintains its own Claude session for context

## 🎯 Use Cases

- **Code Projects**: Create separate projects for different coding tasks
- **Experiments**: Try different approaches in separate threads
- **Learning**: Organize tutorials and learning sessions by topic
- **Prototyping**: Quick experimentation with different ideas

## 🆘 Troubleshooting

### API Connection Issues
If you see "API Connection Failed":
1. Make sure the Flask API is running on port 5000
2. Check the terminal running `python app.py` for errors
3. Verify the `data/projects` directory exists

### Claude CLI Issues
If Claude responses fail:
1. Make sure Claude CLI is installed and authenticated
2. Check that you can run `claude -p "test"` in terminal
3. Verify your API key is set correctly

### UI Issues
If the interface doesn't load properly:
1. Make sure you're using Python 3.8+
2. Try refreshing the browser page
3. Check the Chainlit terminal for error messages

## 🤝 Contributing

This is a hobby project focused on simplicity and functionality. Feel free to:
- Report issues or bugs
- Suggest improvements
- Share your use cases

## 📄 License

This project is open source. See the main project repository for license details.

---

**Happy coding with Claude! 🚀**