# 🎯 Questions to Ask EDEN

## 💬 Chat/Interact Tab Questions

### Basic Greetings & Memory
```
Hello, EDEN
```
```
What do you remember about me?
```
```
Tell me about yourself
```

### User-Specific Questions (Test Memory Retrieval)
```
What do you remember about Ian?
```
```
Tell me about the student
```
```
What interactions have you had with Dr. Smith?
```
```
What do you know about the Judge?
```

### Room & Location Questions
```
Tell me about the kitchen
```
```
What do you know about the living room?
```
```
Describe the office
```
```
What's in the garage?
```
```
Tell me about the bedroom
```
```
What objects are in the bathroom?
```

### Object Questions
```
Where is the red cup?
```
```
Tell me about the toolbox
```
```
What do you know about the sofa?
```
```
Where is the computer monitor?
```

### Interaction & Experience Questions
```
What happened with Ian?
```
```
Tell me about your interactions with the student
```
```
What positive interactions have you had?
```
```
Do you remember picking up the red cup?
```
```
What achievements have you accomplished?
```

### Context-Aware Questions
```
Where did Ian ask me to pick up something?
```
```
What did the student do in the living room?
```
```
What happened in the kitchen?
```

### Personality-Based Questions (After adjusting sliders)
```
How do you feel about helping people?
```
```
What do you think about sudden movements?
```
```
Are you feeling anxious?
```
```
How do you feel right now?
```

---

## 📋 Planning Tab - Goals to Try

### Simple Object Manipulation
**Goal:** `Pick up the red cup from the kitchen counter`  
**User:** `Ian`

**Goal:** `Move the blue book from the office desk to the living room bookshelf`  
**User:** `Student`

**Goal:** `Bring me the toolbox from the garage`  
**User:** (leave empty)

**Goal:** `Get the bicycle from the garage`  
**User:** (leave empty)

### Multi-Step Tasks
**Goal:** `Find the red cup in the kitchen and bring it to the living room coffee table`  
**User:** `Ian`

**Goal:** `Move the computer monitor from the office to the bedroom`  
**User:** (leave empty)

**Goal:** `Navigate from the kitchen to the bedroom and pick up the book on the nightstand`  
**User:** (leave empty)

### Context-Aware Planning
**Goal:** `Pick up the red cup`  
**User:** `Ian`  
*(Uses memories about Ian and kitchen)*

**Goal:** `Help me organize the office desk`  
**User:** `Dr. Smith`

**Goal:** `Clean up the living room`  
**User:** `Student`

### Complex Scenarios
**Goal:** `Navigate from the office to the kitchen, avoiding obstacles, and pick up the red cup`  
**User:** (leave empty)

**Goal:** `Move the sofa in the living room to make space`  
**User:** (leave empty)

**Goal:** `Find all cups in the house and bring them to the kitchen sink`  
**User:** (leave empty)

---

## 🎭 Demo Flow (For Showcase)

### Step 1: Show Memory
Ask: `What do you remember about Ian?`  
*Shows memory retrieval from knowledge graph*

### Step 2: Show Context Awareness
Ask: `Tell me about the kitchen`  
*Shows it knows about kitchen objects and layout*

### Step 3: Show Planning
**Goal:** `Pick up the red cup from the kitchen counter`  
**User:** `Ian`  
*Shows how it uses memories to build scene description*

### Step 4: Show Personality
Adjust Agreeableness slider → Ask: `How do you feel about helping people?`  
*Shows personality affects responses*

### Step 5: Show Graph Growth
After planning/interactions → Check Knowledge Graph tab  
*Shows new nodes added*

---

## 🔥 Best Questions for Testing

### Memory Retrieval
1. `What do you remember about Ian?`
2. `Tell me about the kitchen`
3. `What interactions have you had with the student?`

### Planning Integration
1. `Pick up the red cup from the kitchen counter` (User: Ian)
2. `Move the toolbox from the garage to the office` (User: empty)
3. `Navigate from the living room to the bedroom` (User: empty)

### Personality Effects
1. Set Neuroticism to 0.9 → Ask: `What do you think about sudden movements?`
2. Set Agreeableness to 0.9 → Ask: `How do you feel about helping people?`
3. Set Extroversion to 0.9 → Ask: `Tell me about yourself`

---

## 💡 Tips

1. **Use User Names**: Including "Ian", "Student", "Judge", or "Dr. Smith" helps retrieve user-specific memories

2. **Be Specific**: More specific goals get better plans:
   - ✅ "Pick up the red cup from the kitchen counter"
   - ❌ "Get cup"

3. **Watch the Graph**: After interactions, check Knowledge Graph tab to see new nodes

4. **Planning Takes Time**: Planning requests take ~30-60 seconds with Ollama. Be patient!

5. **Memory Context**: The system uses memories to build scene descriptions. More memories = better context

6. **Personality Matters**: Adjust sliders in Personality tab, then ask questions to see how responses change

---

## 🎯 Quick Test Sequence

1. **Chat:** `What do you remember about Ian?`
2. **Chat:** `Tell me about the kitchen`
3. **Planning:** Goal: `Pick up the red cup from the kitchen counter`, User: `Ian`
4. **Chat:** `What did you just plan?`
5. **Graph:** Check Knowledge Graph tab to see new nodes

