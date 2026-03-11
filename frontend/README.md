# Family Office AI Agent - Frontend

Modern React + TypeScript frontend for the Family Office AI planning system.

## Features

- **Structured Intake Form**: 4-step wizard to capture comprehensive user profile
- **Interactive Chat Interface**: Natural language interaction with AI advisor
- **Visual Breakdowns**: Charts and visualizations for tax, investment, and estate analysis
- **Evidence Panel**: View source documents and citations
- **Responsive Design**: Works on desktop and tablet devices
- **Real-time Updates**: Live updates as AI processes recommendations

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Fast build tool and dev server
- **Recharts** - Data visualization
- **Lucide React** - Icon library
- **Axios** - HTTP client

## Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` if backend runs on different URL:
```
VITE_API_URL=http://localhost:8000
```

## Running the Frontend

### Development Mode

```bash
cd frontend
npm run dev
```

The app will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/         # React components
│   │   ├── IntakeForm.tsx       # 4-step profile wizard
│   │   ├── ChatInterface.tsx    # Chat UI
│   │   ├── BreakdownPanel.tsx   # Analysis visualizations
│   │   └── EvidencePanel.tsx    # Source citations
│   ├── types/              # TypeScript type definitions
│   │   └── index.ts
│   ├── utils/              # Utilities
│   │   └── api.ts               # API client
│   ├── App.tsx             # Main app component
│   ├── main.tsx            # Entry point
│   └── index.css           # Global styles
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## User Flow

1. **Intake Form** (4 steps)
   - Step 1: Basic info (age, income, filing status, state)
   - Step 2: Assets (cash, stocks, bonds, real estate, business)
   - Step 3: Family context (marital status, children, life events)
   - Step 4: Goals and risk preferences

2. **Chat Interface**
   - Ask questions in natural language
   - Receive AI-powered recommendations
   - View conversation history

3. **Analysis Breakdown**
   - Tax optimization strategies
   - Investment allocation chart
   - Estate planning recommendations
   - Supporting evidence with citations

## Component Documentation

### IntakeForm

Multi-step form for collecting user profile data.

```tsx
<IntakeForm onSubmit={(profile) => handleProfileSubmit(profile)} />
```

### ChatInterface

Real-time chat with the AI advisor.

```tsx
<ChatInterface
  messages={messages}
  onSendMessage={async (msg) => await sendMessage(msg)}
  isLoading={isLoading}
/>
```

### BreakdownPanel

Visual breakdown of recommendations.

```tsx
<BreakdownPanel
  breakdown={breakdown}
  modulesUsed={['tax_optimization', 'investment_allocation']}
/>
```

### EvidencePanel

Expandable list of source documents.

```tsx
<EvidencePanel evidence={evidenceList} />
```

## API Integration

The frontend communicates with the backend via REST API:

```typescript
import { apiClient } from '@/utils/api';

// Create session
const { session_id } = await apiClient.createSession();

// Save profile
await apiClient.createProfile(sessionId, profile);

// Send message
const response = await apiClient.sendMessage(sessionId, "What tax strategies should I use?");
```

## Customization

### Styling

All styles are in `src/index.css` using CSS variables for easy theming:

```css
:root {
  --primary-color: #2563eb;
  --bg-primary: #ffffff;
  --text-primary: #0f172a;
  /* ... */
}
```

### Adding New Visualizations

Use Recharts for additional charts:

```tsx
import { BarChart, Bar, XAxis, YAxis } from 'recharts';

<ResponsiveContainer width="100%" height={300}>
  <BarChart data={yourData}>
    <Bar dataKey="value" fill="#2563eb" />
  </BarChart>
</ResponsiveContainer>
```

## Troubleshooting

### CORS Errors

Ensure backend has correct CORS configuration in `.env`:
```
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### API Connection Failed

1. Verify backend is running on port 8000
2. Check `VITE_API_URL` in frontend `.env`
3. Test backend health: `curl http://localhost:8000/health`

### Build Errors

Clear cache and reinstall:
```bash
rm -rf node_modules package-lock.json
npm install
```

## Performance

- Code splitting enabled via Vite
- Lazy loading for heavy components
- Optimized re-renders with React.memo (where needed)
- Efficient chart rendering with Recharts

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (responsive design)
