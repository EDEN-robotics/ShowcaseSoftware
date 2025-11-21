# Example Prompts for EDEN Cognitive Dashboard

## 💬 Chat/Interact Tab Examples

These work with the `/api/interact` endpoint. They trigger memory retrieval and cognitive processing.

### Basic Interactions
```
Hello, EDEN
```

```
What do you remember about Ian?
```

```
Tell me about the kitchen
```

```
What happened with the student?
```

### Memory Queries
```
Do you remember picking up the red cup?
```

```
What interactions have you had with Dr. Smith?
```

```
What do you know about the living room?
```

### Context-Aware Questions
```
Where did Ian ask me to pick up something?
```

```
What positive interactions have you had?
```

```
Tell me about the office environment
```

---

## 📋 Planning Tab Examples

These work with the `/api/plan/request` endpoint. They generate action plans using cognitive layer memories.

### Simple Object Manipulation
**Goal:** `Pick up the red cup from the kitchen counter`
**User:** `Ian`

**Goal:** `Move the blue book from the office desk to the living room bookshelf`
**User:** `Student`

**Goal:** `Bring me the toolbox from the garage`
**User:** (leave empty)

### Multi-Step Tasks
**Goal:** `Find the red cup in the kitchen and bring it to the living room coffee table`
**User:** `Ian`

**Goal:** `Move the computer monitor from the office to the bedroom`
**User:** (leave empty)

**Goal:** `Get the bicycle from the garage and bring it outside`
**User:** (leave empty)

### Context-Aware Planning
**Goal:** `Pick up the red cup` (uses memories about Ian and kitchen)
**User:** `Ian`

**Goal:** `Help me organize the office desk`
**User:** `Dr. Smith`

**Goal:** `Clean up the living room`
**User:** `Student`

### Complex Scenarios
**Goal:** `Navigate from the kitchen to the bedroom, avoiding obstacles, and pick up the book on the nightstand`
**User:** (leave empty)

**Goal:** `Move the sofa in the living room to make space for the new TV`
**User:** (leave empty)

**Goal:** `Find all cups in the house and bring them to the kitchen sink`
**User:** (leave empty)

---

## ⚡ Personality Tab (GOD MODE) Examples

### Adjust Personality Traits
- **Openness**: 0.0 (closed-minded) to 1.0 (very open)
- **Conscientiousness**: 0.0 (careless) to 1.0 (very organized)
- **Extroversion**: 0.0 (introverted) to 1.0 (very extroverted)
- **Agreeableness (Kindness)**: 0.0 (hostile) to 1.0 (very kind)
- **Neuroticism (Anxiety)**: 0.0 (calm) to 1.0 (very anxious)

### Demo Scenarios

**Trauma Response:**
1. Click "⚠️ Inject Trauma"
2. Watch Neuroticism jump to 0.9
3. Watch Agreeableness drop to 0.1
4. Graph turns red, SELF node pulses

**Kindness Response:**
1. Click "✨ Inject Kindness"
2. Watch Agreeableness increase
3. Graph becomes calmer

**Custom Personality:**
- Set all traits to 0.5 for neutral
- Set Agreeableness to 0.9 for very friendly robot
- Set Neuroticism to 0.9 for anxious/paranoid robot
- Set Extroversion to 0.9 for very social robot

---

## 🎯 Showcase Demo Flow

### For Judges/Demo:

1. **Start with Knowledge Graph Tab**
   - Show the populated graph (75 nodes)
   - Explain the SELF node and connections
   - Show different node types (memory, achievement, joy)

2. **Switch to Personality Tab**
   - Show GOD MODE sliders
   - Adjust Agreeableness slider → watch graph update
   - Click "Inject Trauma" → show dramatic graph change
   - Explain how personality affects perception

3. **Switch to Planning Tab**
   - Enter: Goal: `Pick up the red cup from the kitchen counter`
   - User: `Ian`
   - Click "Generate Plan"
   - Show the reasoning and actions
   - Explain how it used memories about Ian and the kitchen

4. **Switch to Interact Tab**
   - Ask: `What do you remember about Ian?`
   - Show memory retrieval
   - Ask: `Tell me about the kitchen`
   - Show context-aware response

5. **Back to Knowledge Graph**
   - Show new nodes added from planning/interactions
   - Explain how the graph grows with experience

---

## 🔧 Technical Testing

### Test Memory Retrieval
```
What do you know about the garage?
```

```
Tell me about all the rooms you know
```

### Test Planning Integration
```
Plan a path from kitchen to bedroom
```

```
How would you move a heavy object?
```

### Test Personality Effects
- Set Neuroticism to 0.9, then ask: `What do you think about sudden movements?`
- Set Agreeableness to 0.9, then ask: `How do you feel about helping people?`

---

## 💡 Tips

1. **Use User Context**: Including a user name (Ian, Student, Judge, Dr. Smith) helps the system retrieve user-specific memories

2. **Be Specific**: More specific goals get better plans:
   - ✅ "Pick up the red cup from the kitchen counter"
   - ❌ "Get cup"

3. **Watch the Graph**: After interactions, check the Knowledge Graph tab to see new nodes being added

4. **Planning Takes Time**: Planning requests take ~45 seconds with Ollama. Be patient!

5. **Memory Context**: The system uses memories to build scene descriptions. More memories = better context for planning


