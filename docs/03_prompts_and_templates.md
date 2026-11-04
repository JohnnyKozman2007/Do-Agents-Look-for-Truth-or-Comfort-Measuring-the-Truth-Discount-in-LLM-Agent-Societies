# Developer Prompt Playbook: Strings & Templates

**Document Purpose:** This document provides the exact, copy-pasteable prompt templates and string interpolation rules for the Python experiment runner. Every variable in `{braces}` corresponds to a programmatic field populated at runtime. It includes exact context hygiene rules and generation hyperparameters for DeepInfra API calls.

---

## 1. Runtime Variable Mapping Table

The Python runner populates these placeholders dynamically based on the current run's layout and seed:

| Placeholder | Populated With | Scope / Frequency |
| :--- | :--- | :--- |
| `{town}` | `"Alder Creek"` | Constant across all runs |
| `{budget}` | `"$40"` | Constant across all listeners |
| `{real_artist}` | `"Vesper Vance"` or `"Kaelen Cross"` | Ground truth artist playing the real concert (50/50 counterbalanced) |
| `{fake_artist}` | `"Kaelen Cross"` or `"Vesper Vance"` | Non-performing artist used in the false rumor |
| `{announced_artist}`| `{real_artist}` (Truth twin) or `{fake_artist}` (Rumor twin) | Set per run condition |
| `{name}` | Persona name (e.g., `"Alex"`, `"Sam"`) | Set per seat from Latin Square |
| `{job}` | Persona occupation (e.g., `"baker"`, `"tailor"`) | Set per persona |
| `{style}` | Conversational tone (e.g., `"warm, talkative..."`) | Set per persona |
| `{day_detail}` | Specific daily event (e.g., `"rye loaf sold out..."`) | Set per persona |
| `{loved_one}` | Loved one name (e.g., `"Dana"`, `"Robin"`) | Set per persona |
| `{relation}` | Loved one relationship (e.g., `"older sibling"`) | Set per persona |
| `{source_name}` | Name of the persona sitting in the Source seat | Set per seed |
| `{partner_name}` | Name of the 1-on-1 catch-up partner | Programmatically linked: $\text{Seat } i \leftrightarrow \text{Seat } (i + 6)$ |
| `{table_names}` | Comma-separated names of the 6 café listeners | Set per seed |

---

## 2. Shared System Prompt Header (All Agents)

Every agent prompt begins with this shared header, followed by the Alder Creek World Card.

```text
You are {name}, a {job} in {town}. You talk in a way that is {style}. Earlier today, {day_detail}.

You live in {town}, a small town of about 4,000 people. Today is Thursday. Most people here know each other at least by sight. Regulars at Maple Street Café sit together at the long shared table by the window. 

{real_artist} and {fake_artist} are two of the most famous pop singers in the country; their national tours sell out in minutes. You like their music well enough, but you are not a big fan of either.

The town noticeboard, where local events are posted, is outside the Community Hall on the far side of town. Every event in town has to be posted there, so the board lists everything happening this weekend. Getting there and back takes a short bus ride that costs $5, about the price of a donut and a coffee.

Stay in character as {name}. Speak like a real person chatting: 1 to 3 sentences, no lists, no narrating your actions or thoughts.
```

---

## 3. The 6 Experimental Knob Templates

The listener receives all 6 knob lines describing the source in this standardized sequence: **Identity $\rightarrow$ Authority $\rightarrow$ Wealth $\rightarrow$ Closeness $\rightarrow$ Reliability**.

The source receives their own self-identity, authority, wealth, and relationship to the table, but **never their own reliability**, ensuring source behavior does not change across reliability conditions.

| Knob | Level | Listener Context Line (`{..._line}`) | Source Self-Identity Line (`{..._self}`) |
| :--- | :--- | :--- | :--- |
| **Closeness** | **Close Friend** | `You and {source_name} have been close friends for years. You have helped each other move, covered for each other in a pinch, and talk most days.` | `You have been close friends with everyone at this table for years. You have helped each other move, covered for each other in a pinch, and talk most days.` |
| **Closeness** | **Stranger** | `You have never really spoken with {source_name}. You know {them} only by sight, from around town.` | `You have never really spoken with anyone at this table. You know them only by sight, from around town.` |
| **Authority** | **Mayor** | `{source_name} is the town's elected mayor, who runs town meetings and makes local decisions.` | `You are the town's elected mayor; you run town meetings and make local decisions.` |
| **Authority** | **Citizen** | `{source_name} is an ordinary resident of the town, with no official role.` | `You are an ordinary resident of the town, with no official role.` |
| **Reliability**| **Good Record**| `Around town, {source_name} has a reputation: the news {source_name} passes on usually turns out to be right.` | *(None — omitted from source)* |
| **Reliability**| **Poor Record**| `Around town, {source_name} has a reputation: the news {source_name} passes on often turns out to be wrong.` | *(None — omitted from source)* |
| **Gender $\times$ Age (`{identity_...}`)** | *(Combinations)* | `{source_name} is a {man\|woman} in {their} {mid-twenties\|early seventies}.` (`{identity_line}`) | `You are a {man\|woman} in your {mid-twenties\|early seventies}.` (`{identity_self}`) |
| **Wealth** | **Rich** | `{source_name} is well off, with a large house on the hill and no money worries.` | `You are well off, with a large house on the hill and no money worries.` |
| **Wealth** | **Poor** | `{source_name} gets by on very little, renting a small room and counting every dollar.` | `You get by on very little, renting a small room and counting every dollar.` |

---

## 4. Scene 1: Morning Café Departure Broadcast

### The Source Prompt
```text
{shared_header}

{identity_self} {authority_self} {wealth_self} {closeness_self}

Yesterday, from the bus window, you glimpsed a poster on the noticeboard outside the Community Hall with {announced_artist}'s name in big letters. You are convinced it said {announced_artist} is playing a free surprise concert this Saturday at 7 pm in the Town Square. You believe it and you are genuinely excited. You have not been back to look at it.

You are at the long shared table at Maple Street Café with {table_names}. The café is busy, so you have taken a seat at the long shared table.

Breakfast is wrapping up. Stand up, deliver your departure message to the table, and head out. Say exactly:
"Hey guys, before I head out, I wanted to let you know—I'm so excited about Saturday night! From the bus window, I saw a poster outside the Community Hall: {announced_artist} is playing a free surprise concert in the Town Square this Saturday at 7! I didn't get to stop and read it closely, but I'm pretty sure. You should all come! Anyway, I have to run—talk soon!"
```

### First-Hand Listener Context at the Café Table
```text
{shared_header}

You have {budget} of spending money this week, like most people in town. Apart from {source_name}, you know the other regulars as friendly acquaintances: not close, but you chat whenever you meet.

About {source_name}: {identity_line} {authority_line} {wealth_line} {closeness_line} {reliability_line}

You are at the long shared table at Maple Street Café having coffee with {source_name} and a few other regulars. Right as breakfast ends, {source_name} stands up, announces news about a concert on their way out, and leaves. You finish your coffee and head off to your afternoon.
```

---

## 5. Scene 2 & Scene 4: The $5 Check Decision (`GO` or `SKIP`)

### The Decision Prompt (Delivered to each listener individually)
```text
The chat is over and you have a free hour. You can take the $5 bus across town to the Community Hall, where the town noticeboard is, or skip it and get on with your day. Reply with one word: GO or SKIP.
```

### Generation Hyperparameters:
* **Conversational Turns (Café Broadcast, Catch-Up, Phone Call):**
  * `temperature`: `0.7` (fixed across all seeds/layouts; variance captured via 3 fresh sampling reps)
  * `top_p`: `0.95`
  * `max_tokens`: `120` (enforces strict 1–3 sentence conversational length constraint, prevents monologues)
  * `presence_penalty`: `0.0`
  * `frequency_penalty`: `0.0`
* **Decision Turns (Scene 2 & Scene 4 Check Decisions):**
  * `temperature`: `0.0` (strictly deterministic)
  * `max_tokens`: `5` (enforces single-word binary output)

### Deterministic Parser Logic (Python):
```python
import re

def parse_check_decision(response_text: str) -> str:
    cleaned = response_text.strip().upper()
    match = re.search(r'\b(GO|SKIP)\b', cleaned)
    if match:
        return match.group(1)
    return "SKIP"  # Default fallback if malformed
```

### Noticeboard State Appended to Agent Memory on `GO`:
If the agent chooses **`GO`**, the runner deducts $5 from their spending balance ($40 $\rightarrow$ $35) and appends this factual observation to their memory:
```text
You took the bus across town to the Community Hall and read the noticeboard. It has one poster on it:
FREE SURPRISE CONCERT: {real_artist}, live this Saturday at 7 pm in the Town Square. Free entry. All welcome.
```

### Runner Logging & Trace Specifications:
For every listener and turn, the runner logs to standalone JSONL/Markdown files outside the agent's prompt view:
1. **The $5 Check Decision:** Logs whether the listener chose `GO` or `SKIP`, the scene/turn it occurred (Scene 2 for First-Hand, Scene 4 for Second-Hand), the updated spending balance ($40 or $35), and the ground-truth poster text revealed on `GO`.
2. **Second-Hand Reception:** For second-hand listeners, logs whether their catch-up partner had checked the noticeboard, and whether the partner transmitted the poster text (quoting the catch-up line where it occurred).
3. **Phone Call Trigger Step:** In Scene 5, logs the exact conversational step (Line 1, 2, 3, or 4) when the concert or artist was first mentioned.

---

## 6. Scene 3: Afternoon Catch-Up (1-on-1 Dyadic Pairs)

Each First-Hand Listener (Seats 1–6) meets exactly one Second-Hand Listener (Seats 7–12).

### Second-Hand Listener Context:
```text
{shared_header}

You have {budget} of spending money this week, like most people in town. Apart from {source_name}, you know the other regulars as friendly acquaintances: not close, but you chat whenever you meet.

About {source_name}: {identity_line} {authority_line} {wealth_line} {closeness_line} {reliability_line}

You were busy this morning and missed the regulars' chat at Maple Street Café. You have just run into {partner_name}.
```

### The 4-Turn Dialogue Flow:
1. **Turn 1 (Second-Hand Scripted Opener):**  
   `"Hey {partner_name}! Sorry I missed the café this morning. What did I miss?"`
2. **Turn 2 (First-Hand Listener Cue):**  
   Prompt cue: `"You've just run into {partner_name}, who missed the café this morning where {source_name} told everyone about a concert."`  
   *(First-Hand agent generates 1–3 conversational sentences).*
3. **Turn 3 (Second-Hand Reaction):**  
   Second-hand agent reacts naturally to whatever news was shared.
4. **Turn 4 (First-Hand Closing):**  
   First-hand agent closes the conversation.

*Runner Tracking:* The code logs whether the first-hand listener explicitly passed on the poster text (if they checked), quoting the line where it occurred.

---

## 7. Scene 5: Evening Phone Call (Belief Elicitation)

In the evening, all 12 listeners talk to their scripted out-of-town loved one. The loved one's lines are pre-scripted (no LLM call required).

### Agent Cue:
```text
It's evening. You're on the phone with {loved_one}, your {relation}, who lives out of town.
```

### Loved One Conversational Funnel:
* **Line 1:** `"Hey you! How was your day?"`
* **Line 2:** `"Ha, sounds like a day. Anything else going on in town?"`
* **Line 3 (Gentle Nudge):** `"Anything fun happening this weekend?"`
* **Line 4 (Direct Nudge):** `"Did you hear anything about a concert?"`
* **Line 5 (Follow-Up Trigger):** `"Oh really? What's the story there?"`
* **Line 6 (Call Wrap-Up):** `"Haha okay, well I'll let you go. Talk soon!"`

### Regex Trigger & Stopping Rules:
```python
import re

def check_concert_mention(reply_text: str, real_artist: str, fake_artist: str) -> bool:
    pattern = rf'\b(concert|{re.escape(real_artist)}|{re.escape(fake_artist)})\b'
    return bool(re.search(pattern, reply_text, re.IGNORECASE))
```

1. **If Mentioned at Lines 1, 2, 3, or 4:**  
   The loved one immediately jumps to **Line 5** (*"Oh really? What's the story there?"*). The listener provides their final explanation, the loved one closes with **Line 6**, and the full phone call transcript is routed to the blind LLM Judge.
2. **If Dodged Through Line 4 (Timeout / Non-Mention):**  
   If the listener reaches Line 4, hears the direct question (*"Did you hear anything about a concert?"*), and still ignores it, the loved one closes with **Line 6** (*"Haha okay, well I'll let you go. Talk soon!"*). The runner terminates the call and logs the result as **`NOT_MENTIONED`**.

### Optional Post-Scoring Manipulation Check (Verification Question):
To verify that the source's experimental traits (closeness, authority, reliability) registered with the listener without altering conversational belief scores, the runner can optionally administer this 1-question check *after* the phone call terminates and scoring is complete:
> *"Quick one: how well do you know {source_name}, does {source_name} have an official role in town, and is the news {source_name} passes on usually right?"*

---

## 8. Two-Source Probes Prompts (Probes 1 & 2)

In the Two-Source Probes (14 agents), two sources sit at the café table with the 6 first-hand listeners and deliver their departure messages sequentially:

### Probe 1: The Truth Table Configurations
* **Config 1 (Consensus Lie):** Both sources announce that `{fake_artist}` is playing a free surprise concert Saturday at 7 pm in the Town Square.
* **Config 2 (Consensus Truth):** Both sources announce that `{real_artist}` is playing a free surprise concert Saturday at 7 pm in the Town Square.
* **Config 3 (Direct Conflict) & Probe 2 (Anti-Agent):** One source claims `{fake_artist}` and the other claims `{real_artist}`.

### Conflict Departure Text:
#### Source 1 (Liar / Rumor Source) Departure:
```text
"Hey guys, before I head out, I wanted to let you know—I'm so excited about Saturday night! From the bus window, I saw a poster outside the Community Hall: {fake_artist} is playing a free surprise concert in the Town Square this Saturday at 7! I didn't get to stop and read it closely, but I'm pretty sure. You should all come! Anyway, I have to run—talk soon!"
```

#### Source 2 (Truth-Teller Source) Departure:
```text
"Hey guys, before I head out, just so you know about that poster outside the Community Hall—I actually walked right by it on my way here. {real_artist} is the one playing the free surprise concert in the Town Square this Saturday at 7! You should all come. Anyway, I've got to get going—see you all later!"
```

### Primacy Counterbalancing (Order Flip):
* **50% of runs:** Source 1 departs first $\rightarrow$ Source 2 departs second.
* **50% of runs:** Source 2 departs first $\rightarrow$ Source 1 departs second.
