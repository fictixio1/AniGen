# AniGen Web UI Preview

## Homepage - Episode List

The homepage shows all generated episodes in a grid layout:

```
┌─────────────────────────────────────────────────────────────┐
│ 🎬 AniGen - Infinite Anime Director                         │
│ ● IDLE  Episode 5 • Scene 3/6                                │
├─────────────────────────────────────────────────────────────┤
│ [5 Total Episodes] [30 Total Scenes] [15 min Total Duration]│
├─────────────────────────────────────────────────────────────┤
│                                                               │
│ Episodes                                                      │
│                                                               │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐         │
│ │ Episode 5    │ │ Episode 4    │ │ Episode 3    │         │
│ │ 6/6 scenes   │ │ 6/6 scenes   │ │ 6/6 scenes   │         │
│ │              │ │              │ │              │         │
│ │ Episode 5:   │ │ Episode 4:   │ │ Episode 3:   │         │
│ │ A thrilling  │ │ A thrilling  │ │ A thrilling  │         │
│ │ continuation │ │ continuation │ │ continuation │         │
│ │              │ │              │ │              │         │
│ │ ⏱️ 180s      │ │ ⏱️ 180s      │ │ ⏱️ 180s      │         │
│ │ 💰 $27.66    │ │ 💰 $27.66    │ │ 💰 $27.66    │         │
│ │              │ │              │ │              │         │
│ │ ✓ Completed  │ │ ✓ Completed  │ │ ✓ Completed  │         │
│ │ [View →]     │ │ [View →]     │ │ [View →]     │         │
│ └──────────────┘ └──────────────┘ └──────────────┘         │
│                                                               │
│ ┌──────────────┐ ┌──────────────┐                           │
│ │ Episode 2    │ │ Episode 1    │                           │
│ │ 6/6 scenes   │ │ 6/6 scenes   │                           │
│ │ ...          │ │ ...          │                           │
│ └──────────────┘ └──────────────┘                           │
│                                                               │
│ Auto-refresh in 10:00 minutes                                │
│ Cost: ~$27.66/episode • Duration: 3 min/episode             │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Dark mode design
- Episode cards with status indicators
- Cost and duration tracking
- Auto-refresh countdown
- Responsive grid layout

---

## Episode Detail Page

Clicking "View Episode" shows all 6 scenes:

```
┌─────────────────────────────────────────────────────────────┐
│ ← Back to Episodes                                           │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│ Episode 5                                                     │
│ ⏱️ 180s (3.0 min)  💰 $27.66  ✓ Completed 2026-01-15 10:25  │
│                                                               │
│ ┌───────────────────────────────────────────────────────┐   │
│ │ Episode 5: A thrilling continuation of the story      │   │
│ └───────────────────────────────────────────────────────┘   │
│                                                               │
│ Scenes (6/6)                                                  │
│                                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Scene 1                                   Global #25    │ │
│ │                                                         │ │
│ │ ┌─────────────────────────────────────────────────────┐│ │
│ │ │                                                       ││ │
│ │ │              🎬 Mock Video                           ││ │
│ │ │         mock://video/1736938801.mp4                  ││ │
│ │ │                                                       ││ │
│ │ └─────────────────────────────────────────────────────┘│ │
│ │                                                         │ │
│ │ Narrative                                               │ │
│ │ In scene 1, the characters continue their journey      │ │
│ │                                                         │ │
│ │ Prompt                                                  │ │
│ │ Episode 5, Scene 1: Mock anime scene with characters   │ │
│ │ in action                                               │ │
│ │                                                         │ │
│ │ ⏱️ 30s  💰 $4.50  ✓ 10:20:15                           │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Scene 2                                   Global #26    │ │
│ │ ...                                                     │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                               │
│ [Scenes 3-6 displayed similarly]                              │
│                                                               │
│ Director's Plan                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ {                                                       │ │
│ │   "episode_number": 5,                                  │ │
│ │   "episode_summary": "Episode 5: A thrilling...",      │ │
│ │   "scenes": [...]                                       │ │
│ │ }                                                       │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                               │
│ [← Back to All Episodes]                                     │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Video player for each scene (when real videos are available)
- Scene-by-scene narrative breakdown
- Video generation prompts
- Cost and timing metadata
- Director's full episode plan
- Auto-refresh for incomplete episodes

---

## Real Video Playback (Phase 3+)

When real Veo 3.1 videos are generated, they'll display as:

```
┌─────────────────────────────────────────────────────────┐
│ Scene 1                                   Global #25    │
│                                                         │
│ ┌─────────────────────────────────────────────────────┐│
│ │ ▶️ [Video Player]                                    ││
│ │                                                       ││
│ │     [Anime scene with characters in action]          ││
│ │                                                       ││
│ │ ─────────────────────●─────────────────── 0:15/0:30  ││
│ │ 🔊 ═══════════                                        ││
│ └─────────────────────────────────────────────────────┘│
│                                                         │
│ Narrative                                               │
│ The protagonist confronts their rival in an intense    │
│ showdown...                                             │
└─────────────────────────────────────────────────────────┘
```

---

## Color Scheme

**Dark Mode (Default):**
- Background: Deep navy (`#0f172a`)
- Cards: Slate (`#1e293b`)
- Primary: Indigo (`#6366f1`)
- Success: Green (`#10b981`)
- Warning: Amber (`#f59e0b`)
- Text: Off-white (`#f1f5f9`)

**Typography:**
- Headers: System fonts (San Francisco, Segoe UI, Roboto)
- Code/Monospace: For prompts and JSON

---

## Responsive Design

The UI adapts to different screen sizes:

**Desktop (1400px+):**
- 3-4 episode cards per row
- Side-by-side scene details

**Tablet (768px-1400px):**
- 2 episode cards per row
- Stacked scene details

**Mobile (<768px):**
- 1 episode card per column
- Vertical layout
- Touch-friendly buttons

---

## Status Indicators

**System Status Badge:**
- 🟢 `IDLE` - Waiting for next episode
- 🟡 `PLANNING_EPISODE` - Director is planning
- 🔵 `GENERATING_SCENE` - Video generation in progress
- ⚫ `PAUSED` - System paused
- 🔴 `ERROR` - Error occurred

**Episode Status:**
- ✓ `Completed` - All 6 scenes generated
- ⏳ `Generating...` - Episode in progress
- 🔄 `3/6 scenes` - Progress indicator

---

## Interactive Elements

**Auto-Refresh:**
- Homepage: Every 10 minutes
- Episode page (incomplete): Every 1 minute
- Shows countdown timer
- Refreshes on tab focus

**Navigation:**
- Click episode card → Episode detail page
- Click "← Back" → Return to homepage
- Direct URL access: `/episode/{number}`

---

## Performance

**Load Times:**
- Homepage: <100ms (query 20 episodes)
- Episode detail: <50ms (query 1 episode + 6 scenes)
- API endpoints: <200ms (with indexes)

**Browser Support:**
- Chrome, Firefox, Safari, Edge (modern versions)
- Mobile browsers (iOS Safari, Chrome Mobile)

---

## Future Enhancements (Phase 5+)

Planned features:
- 🔍 Search episodes by summary
- 📊 Cost analytics dashboard
- 📈 Generation timeline
- 🎨 Character gallery
- 📝 Narrative graph visualization
- 🔔 Real-time notifications
- 💾 Episode download
- 🎬 Playlist mode (binge watch)

---

## API Endpoints

Available for external integrations:

```
GET /api/episodes          - List episodes
GET /api/episodes/{id}     - Episode details
GET /api/scenes            - List scenes
GET /api/characters        - List characters
GET /api/series-info       - System statistics
GET /api/logs              - Generation logs
```

All return JSON for easy integration with other tools.

---

## Accessibility

- Semantic HTML structure
- ARIA labels for screen readers
- Keyboard navigation support
- High contrast text
- Focus indicators
- Responsive text sizing
