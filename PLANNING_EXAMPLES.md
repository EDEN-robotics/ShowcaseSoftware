# 🎯 Planning Tab - Best Goals to Try

## Quick Start Examples

### ✅ Best for Demo (Simple & Fast)

**1. Classic Red Cup**
- **Goal:** `Pick up the red cup from the kitchen counter`
- **User:** `Ian`
- **Why:** Uses memories about Ian and kitchen, shows context awareness

**2. Toolbox Move**
- **Goal:** `Move the toolbox from the garage to the office`
- **User:** (leave empty)
- **Why:** Simple, clear, uses spatial knowledge

**3. Book Transport**
- **Goal:** `Bring the blue book from the office desk to the living room bookshelf`
- **User:** `Student`
- **Why:** Multi-step, shows planning capability

---

## 📋 By Category

### Simple Object Manipulation

**Pick up objects:**
- `Pick up the red cup from the kitchen counter` (User: Ian)
- `Get the toolbox from the garage` (User: empty)
- `Pick up the book on the nightstand` (User: empty)

**Move objects:**
- `Move the blue book from the office desk to the living room bookshelf` (User: Student)
- `Move the computer monitor from the office to the bedroom` (User: empty)
- `Bring the bicycle from the garage outside` (User: empty)

### Multi-Step Navigation

**Navigate + Pick up:**
- `Navigate from the kitchen to the bedroom and pick up the book on the nightstand` (User: empty)
- `Go from the office to the kitchen and get the red cup` (User: Ian)
- `Walk from the living room to the garage and bring back the toolbox` (User: empty)

**Complex paths:**
- `Navigate from the office to the kitchen, avoiding obstacles, and pick up the red cup` (User: empty)
- `Go from the bedroom through the living room to the kitchen` (User: empty)

### Context-Aware Planning (Uses Memories)

**User-specific:**
- `Pick up the red cup` (User: Ian) - *Uses memories about Ian and kitchen*
- `Help me organize the office desk` (User: Dr. Smith)
- `Clean up the living room` (User: Student)

**Memory-based:**
- `Do what Ian asked me to do earlier` (User: Ian)
- `Complete the task from the kitchen` (User: empty)

### Complex Scenarios

**Multi-object:**
- `Find all cups in the house and bring them to the kitchen sink` (User: empty)
- `Move the sofa in the living room to make space for the new TV` (User: empty)
- `Organize the office desk and move files to the filing cabinet` (User: empty)

**Spatial reasoning:**
- `Navigate around obstacles from the garage to the office` (User: empty)
- `Move heavy objects carefully from the garage to the living room` (User: empty)

---

## 🎭 Demo Flow Suggestions

### Quick Demo (2-3 minutes)
1. **Goal:** `Pick up the red cup from the kitchen counter`  
   **User:** `Ian`  
   *Shows memory retrieval and context-aware planning*

2. **Goal:** `Move the toolbox from the garage to the office`  
   **User:** (empty)  
   *Shows spatial reasoning*

### Full Demo (5-10 minutes)
1. Start with simple: `Pick up the red cup` (User: Ian)
2. Show multi-step: `Navigate from kitchen to bedroom and get the book` (User: empty)
3. Show complex: `Find all cups and bring them to kitchen sink` (User: empty)

---

## 💡 Tips

1. **Be Specific:** 
   - ✅ "Pick up the red cup from the kitchen counter"
   - ❌ "Get cup"

2. **Use User Names:** Including "Ian", "Student", "Judge", or "Dr. Smith" helps retrieve user-specific memories

3. **Include Locations:** Mentioning rooms (kitchen, office, garage) helps with spatial planning

4. **Wait for Response:** Planning takes ~30-60 seconds with Ollama. Be patient!

5. **Watch the Graph:** After planning, check Knowledge Graph tab to see new nodes added

---

## 🔥 Top 5 Best Goals

1. **`Pick up the red cup from the kitchen counter`** (User: Ian)
   - Classic demo, uses memories

2. **`Move the toolbox from the garage to the office`** (User: empty)
   - Simple, clear, fast

3. **`Navigate from the kitchen to the bedroom and pick up the book`** (User: empty)
   - Shows multi-step planning

4. **`Bring the blue book from the office desk to the living room bookshelf`** (User: Student)
   - Uses spatial knowledge

5. **`Find all cups in the house and bring them to the kitchen sink`** (User: empty)
   - Complex, impressive

---

## ⚠️ What to Avoid

- Too vague: "Get stuff" ❌
- No location: "Pick up cup" ❌ (better: "Pick up cup from kitchen")
- Unrealistic: "Fly to the moon" ❌
- Too complex: "Build a house" ❌

Stick to objects and locations that exist in the test knowledge graph!

