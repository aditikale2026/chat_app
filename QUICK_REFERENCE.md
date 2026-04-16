# 🚀 Frontend Quick Reference Card

## Getting Started (2 minutes)

```bash
# Navigate to project
cd /home/my/Desktop/Chatapp

# Install dependencies (first time only)
npm install

# Start dev server
npm run dev

# Open browser
# http://localhost:5173
```

## Common Commands

| Command | Purpose |
|---------|---------|
| `npm run dev` | Start development server (HMR enabled) |
| `npm run build` | Build production assets |
| `npm run preview` | Preview production build |
| `npm install` | Install/update dependencies |
| `./START_FRONTEND.sh` | Interactive menu for commands |

## Project Structure at a Glance

```
src/                    → React source code
├── App.jsx             → Main app & routing
├── main.jsx            → Entry point
├── index.css           → Styles (Tailwind)
├── pages/              → Page components
│   ├── LoginPage.jsx
│   ├── RegisterPage.jsx
│   ├── ChatPage.jsx
│   └── UploadPage.jsx
├── components/         → Reusable components
├── context/            → Auth state
└── utils/              → API client

app/static/dist/        → Production build (generated)
```

## Key Files to Edit

| File | Purpose | Change For |
|------|---------|-----------|
| `src/utils/api.js` | API endpoints | Backend URL changes |
| `tailwind.config.js` | Colors & theme | Dark mode customization |
| `src/pages/*.jsx` | Pages | UI modifications |
| `src/components/*.jsx` | Components | Reusable UI updates |
| `src/index.css` | Global styles | Custom animations |

## API Endpoints

```javascript
// Authentication
POST /ui/login              → Login user
POST /ui/register           → Register user
POST /ui/logout             → Logout user

// RAG Chat
POST /rag/query             → Ask question
POST /rag/upload            → Upload document
GET  /health                → Health check

// Usage in components
import { ragAPI, authAPI } from '../utils/api'

// Chat
await ragAPI.query("question")
await ragAPI.upload(file)

// Auth
await authAPI.login(username, password)
await authAPI.logout()
```

## Component Usage Examples

### Using Authentication
```jsx
import { useAuth } from '../context/AuthContext'

export const MyComponent = () => {
  const { user, login, logout } = useAuth()
  
  if (!user?.authenticated) return <Redirect to="/login" />
  
  return <div>Welcome!</div>
}
```

### Making API Calls
```jsx
import { ragAPI } from '../utils/api'
import { useState } from 'react'

export const MyChat = () => {
  const [response, setResponse] = useState('')
  
  const ask = async (query) => {
    try {
      const res = await ragAPI.query(query)
      setResponse(res.data.answer)
    } catch (err) {
      console.error(err)
    }
  }
  
  return <button onClick={() => ask('hello')}>Ask</button>
}
```

### Using Icons
```jsx
import { Send, Upload, LogOut } from 'lucide-react'

<Send size={20} className="text-blue-500" />
<Upload size={24} />
<LogOut size={18} className="text-red-500" />
```

### Protected Routes
```jsx
import { ProtectedRoute } from './components/ProtectedRoute'

<Route
  path="/chat"
  element={
    <ProtectedRoute>
      <ChatPage />
    </ProtectedRoute>
  }
/>
```

## Styling with Tailwind

### Common Classes
```jsx
{/* Layout */}
<div className="flex gap-4">
<div className="grid grid-cols-2 gap-4">
<div className="sticky top-0 z-50">

{/* Sizing */}
<div className="w-full h-screen">
<button className="px-4 py-2">

{/* Colors */}
<div className="bg-dark text-white">
<button className="bg-blue-600 hover:bg-blue-700">

{/* Responsive */}
<div className="hidden sm:block">
<div className="text-sm md:text-base lg:text-lg">

{/* Effects */}
<div className="rounded-lg shadow-lg">
<button className="transition hover:opacity-50">
```

## Debugging

### Browser DevTools
1. **Console**: Check for JavaScript errors
2. **Network**: Verify API calls work
3. **React DevTools**: Inspect component state
4. **Application**: Check cookies for auth token

### Common Issues

| Problem | Solution |
|---------|----------|
| Blank page | Clear cache, check console |
| API fails | Ensure backend running on 8000 |
| Styles missing | Run `npm run build` again |
| Auth issues | Check browser cookies for token |

## Deployment

### Quick Deploy
```bash
# Build
npm run build

# The app is now in app/static/dist/
# Run backend - it serves the frontend automatically
python -m uvicorn app.main:rag_api --host 0.0.0.0 --port 8000

# Visit: http://localhost:8000
```

## Useful Links

- [React Docs](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [Lucide Icons](https://lucide.dev)
- [React Router](https://reactrouter.com)
- [Axios Docs](https://axios-http.com)

## Dependencies

```json
{
  "dependencies": {
    "react": "^18",
    "react-dom": "^18",
    "react-router-dom": "^6",
    "axios": "latest",
    "lucide-react": "latest"
  },
  "devDependencies": {
    "vite": "^4",
    "@vitejs/plugin-react": "^4",
    "tailwindcss": "^3",
    "postcss": "^8",
    "autoprefixer": "^10"
  }
}
```

## Port Numbers

| Service | Port | URL |
|---------|------|-----|
| Dev Server | 5173 | http://localhost:5173 |
| Backend | 8000 | http://localhost:8000 |
| Preview | 4173 | http://localhost:4173 |

## Size Reference

- Production JS: ~87KB gzipped
- Production CSS: ~3.5KB gzipped
- Build time: ~6 seconds
- Dev server startup: ~500ms with HMR

## Pro Tips

✨ **Performance**
- Use React DevTools to check unnecessary re-renders
- Code-split pages for faster load times
- Lazy load icons with dynamic imports

�� **Styling**
- Use Tailwind's @apply for repeated patterns
- Custom CSS only when necessary
- Keep component styles in components

🔐 **Security**
- Never commit secrets to git
- Always use HTTPS in production
- Validate file uploads on backend

📱 **Mobile**
- Test on real devices
- Use DevTools device emulation
- Consider touch targets (44px minimum)

## Support Resources

📄 **Documentation:**
- `FRONTEND_README.md` - Full feature docs
- `FRONTEND_SETUP.md` - Setup guide
- `FRONTEND_DESIGN.md` - Design system
- `FRONTEND_SUMMARY.txt` - Detailed summary

🆘 **Getting Help:**
1. Check the docs above
2. Look at example components in src/pages/
3. Check browser console for errors
4. Review network requests in DevTools

---

**Happy coding! 🚀**

For full documentation, see FRONTEND_README.md
