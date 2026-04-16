# RAG Chat Frontend - Modern React UI

A beautiful, interactive React-based frontend for the RAG Chat application. Features real-time chat, document uploads, user authentication, and a clean, responsive design.

## 🎨 Features

- **Modern Dark UI** - Clean, professional dark theme with gradient accents
- **Real-time Chat** - Interactive chat interface with streaming support
- **Document Management** - Upload PDFs and TXT files for RAG queries
- **User Authentication** - Secure login/registration system
- **Rate Limiting** - Client-side feedback for API rate limits
- **Responsive Design** - Works seamlessly on desktop, tablet, and mobile
- **Smooth Animations** - Fade-in effects and loading states
- **Error Handling** - User-friendly error messages and alerts

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

### Development Server

The development server runs on `http://localhost:5173` with hot module reloading.

```bash
npm run dev
```

### Production Build

Creates an optimized production build in `app/static/dist/`:

```bash
npm run build
```

## 📁 Project Structure

```
src/
├── main.jsx                 # React entry point
├── App.jsx                  # Main app component with routing
├── index.css               # Tailwind CSS + custom styles
├── components/
│   ├── Navbar.jsx          # Navigation bar with logout
│   └── ProtectedRoute.jsx   # Route protection wrapper
├── pages/
│   ├── LoginPage.jsx        # User login page
│   ├── RegisterPage.jsx     # User registration page
│   ├── ChatPage.jsx         # Main chat interface
│   └── UploadPage.jsx       # Document upload interface
├── context/
│   └── AuthContext.jsx      # Authentication state management
└── utils/
    └── api.js              # Axios API client
```

## 🔐 Authentication Flow

1. **Guest Access** → Redirected to `/login`
2. **Login/Register** → Credentials sent to backend, token stored in cookies
3. **Protected Routes** → `ProtectedRoute` component checks for `access_token` cookie
4. **Auto-Logout** → Invalid/expired token redirects to login

## 📡 API Integration

### Chat Query
```javascript
// POST /rag/query
await ragAPI.query("What is the main topic?")
// Response: { answer, sources }
```

### File Upload
```javascript
// POST /rag/upload (multipart/form-data)
await ragAPI.upload(file)
// Response: success/error
```

### Authentication
```javascript
// POST /ui/login
await authAPI.login(username, password)

// POST /ui/register
await authAPI.register(username, password)

// POST /ui/logout
await authAPI.logout()
```

## 🎨 Styling

- **Framework**: Tailwind CSS v3
- **Icons**: Lucide React
- **Color Scheme**: Dark mode with blue/purple accents
- **Custom CSS**: Animations and scrollbar styling

### Custom Tailwind Colors
```javascript
// Dark theme
bg-dark:    #0f1419
bg-darker:  #0a0e13
```

## 🔧 Development Guide

### Adding a New Page

1. Create component in `src/pages/NewPage.jsx`
2. Add route in `src/App.jsx`
3. Import and use `<ProtectedRoute>` if needed
4. Use `Navbar` component for consistency

### Using Lucide Icons

```jsx
import { Icon } from 'lucide-react'

<Icon size={24} className="text-blue-500" />
```

### Making API Calls

```jsx
import { ragAPI } from '../utils/api'

const response = await ragAPI.query("question")
const { answer, sources } = response.data
```

## 📱 Responsive Design

- **Mobile**: Optimized for phones (320px+)
- **Tablet**: Full features on tablets (768px+)
- **Desktop**: Enhanced layout on desktop (1024px+)

Navigation buttons hide text on mobile, showing only icons.

## ⚙️ Configuration

### Vite Config
- **Port**: 5173 (dev)
- **Output**: `app/static/dist/`
- **Proxy**: Backend requests to `http://localhost:8000`

### API Base URL
Change in `src/utils/api.js`:
```javascript
const API = axios.create({
  baseURL: 'http://your-api-url',
  withCredentials: true,
})
```

## 🐛 Troubleshooting

### Build Fails
- Clear `node_modules`: `rm -rf node_modules && npm install`
- Check Node version: `node -v` (requires 18+)

### API Calls Fail
- Ensure backend is running on `http://localhost:8000`
- Check CORS settings in FastAPI backend
- Verify credentials in cookies

### Styles Not Loading
- Run `npm run build` to regenerate CSS
- Clear browser cache
- Check `app/static/dist/` exists

## 📦 Dependencies

- **react@18**: UI framework
- **react-router-dom@6**: Client-side routing
- **axios**: HTTP client
- **tailwindcss@3**: CSS framework
- **lucide-react**: Icon library
- **vite@4**: Build tool

## 🎯 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 📝 License

Part of the RAG Chat Application. Built with React + Vite.
