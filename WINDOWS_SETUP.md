# Windows Setup Guide for Claude Web Runner

## 🐛 Quick Fix for Pydantic/Chainlit Error

If you're getting a Pydantic error when running `start_app.py`, here's the solution:

### ⚡ **Quick Start (Recommended)**

1. **Use the simple runner:**
   ```cmd
   python run_simple.py
   ```

2. **Or run manually (2 terminals):**
   
   **Terminal 1 - Backend:**
   ```cmd
   python app.py
   ```
   
   **Terminal 2 - Frontend:**
   ```cmd
   chainlit run chainlit_app.py
   ```

3. **Open browser:** http://localhost:8000

## 🔧 **Fix Dependency Issues**

If you're still having problems:

```cmd
# Upgrade packages
pip install --upgrade chainlit pydantic

# Or reinstall fresh
pip uninstall chainlit pydantic
pip install chainlit>=1.3.0 pydantic>=2.0.0
```

## 🎯 **Step-by-Step Windows Setup**

### 1. **Prerequisites**
- Python 3.8+ installed
- Git installed
- Claude CLI: `npm install -g @anthropic-ai/claude-code`

### 2. **Clone and Setup**
```cmd
git clone https://github.com/liamgwallace/claude_web.git
cd claude_web
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. **Start Application**
```cmd
# Option 1: Simple runner
python run_simple.py

# Option 2: Manual (recommended for development)
# Terminal 1:
python app.py

# Terminal 2: 
chainlit run chainlit_app.py
```

### 4. **Access Application**
- Application (API + Web Interface): http://localhost:8000

## 🆘 **Common Windows Issues**

### **Issue: "chainlit command not found"**
```cmd
# Install chainlit globally or use python -m
pip install chainlit
# Or run with: python -m chainlit run chainlit_app.py
```

### **Issue: "claude command not found"**
```cmd
# Install Claude CLI
npm install -g @anthropic-ai/claude-code

# Authenticate
claude auth
```

### **Issue: Port already in use**
```cmd
# Kill processes on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F
```

## 🎉 **Verification**

Once running, you should see:
- ✅ Flask: "Starting Claude Web API on port 8000"  
- ✅ Browser: Claude Web Runner interface loads at http://localhost:8000

## 💡 **Tips**

- **Use `start.py`** for the easiest startup experience
- **Single server** - no need to manage multiple terminals
- **Port 8000** is the only port you need to remember
- **Check firewall settings** if having connection issues

## 🐛 **Still Having Issues?**

1. Check Python version: `python --version` (need 3.8+)
2. Verify virtual environment is activated
3. Try running components separately
4. Check the GitHub issues page for updates

**Happy coding with Claude! 🚀**