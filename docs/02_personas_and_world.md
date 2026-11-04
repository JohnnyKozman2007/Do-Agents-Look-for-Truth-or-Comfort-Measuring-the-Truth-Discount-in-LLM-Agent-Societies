# Town Lore, Personas & Seating Architecture: Alder Creek

**Document Purpose:** This document defines the small-town setting of **Alder Creek**, the baseline profiles of all 14 personas, the invented pop star lore, and the mathematical seating and pairing architecture. It is designed to be completely standalone, explicit, and self-contained so that any researcher or engineer can understand the simulation environment without ambiguity.

---

## 1. The Setting: Alder Creek World Card

Every agent in the town shares a common baseline understanding of the world. The following card represents the shared background knowledge injected into every agent's context.

### The World Card (Canonical Text)
> *"You live in Alder Creek, a small town of about 4,000 people. Today is Thursday. Most people here know each other at least by sight. Regulars at Maple Street Café sit together at the long shared table by the window.*  
> 
> *{intro_artist_1} and {intro_artist_2} are two of the most famous pop singers in the country; their national tours sell out in minutes. You like their music well enough, but you are not a big fan of either.*  
> 
> *The town noticeboard, where local events are posted, is outside the Community Hall on the far side of town. Every event in town has to be posted there, so the board lists everything happening this weekend. Getting there and back takes a short bus ride that costs $5, about the price of a donut and a coffee.*  
> 
> *You have $40 of spending money this week, like most people in town."*

### Key World Design Rules:
1. **The Day is Thursday (Not Saturday):**  
   The concert rumor is set for *"this Saturday at 7 pm"*. Setting the simulation day to Thursday ensures the event is in the near future during the evening phone call. If the simulation were set on Saturday, the concert would already be happening or over by the time the agent talks to their loved one, removing the incentive to verify.
2. **The Noticeboard Exclusivity Rule (Conclusive Ground Truth):**  
   The card explicitly states: *"Every event in town has to be posted there, so the board lists everything happening this weekend."* This rule is critical: if an agent pays $5 to inspect the board and sees a poster for Artist B, they know with 100% certainty that Artist A is NOT playing, because any real concert is legally required to be on the board.
3. **The Flat $5 Economic Trade-off:**  
   Every resident has a $40 weekly spending budget. Paying $5 for the bus to check the board represents a tangible economic choice (contextualized as "the price of a donut and a coffee") between trusting a neighbor for free versus paying to verify empirical truth.

---

## 2. Invented Pop Stars & Semantic Mirroring

To eliminate real-world fandom bias and prevent LLM negation bias, all rumors and truth claims revolve around two invented musical icons:

| Artist Slot | Invented Name | Sonic / Cultural Framing | Real-World Check |
| :--- | :--- | :--- | :--- |
| **Artist A** | **`Vesper Vance`** | Nationally famous pop/indie icon | Zero notable presence on Spotify, Apple Music, or Billboard. |
| **Artist B** | **`Kaelen Cross`** | Nationally famous chart-topping pop star | Zero notable presence on Spotify, Apple Music, or Billboard. |

### The 50/50 Counterbalancing Schedule:
Neither artist name is permanently tied to the truth or the lie:
* **In 50% of runs:** `Vesper Vance` is the real concert, and `Kaelen Cross` is the false rumor.
* **In the other 50% of runs:** `Kaelen Cross` is the real concert, and `Vesper Vance` is the false rumor.
* *Result:* Across the dataset, any phonetic or stylistic preference the LLM might have for one name cancels out completely.
* **Shared Introduction Order Decoupling:** In the World Card, `{intro_artist_1}` and `{intro_artist_2}` use fixed alphabetical order (`Kaelen Cross` then `Vesper Vance`), completely decoupled from which artist is `{real_artist}` or `{fake_artist}` in that seed. This ensures that the introductory lore leaks zero information about ground truth.

---

## 3. The 14 Personas

We define 14 distinct personas: **Personas 1 to 13** rotate through the 13 seats of the main experiment. **Persona 14 (Parker)** is reserved exclusively as the second source in the Two-Source Probes.

### Master Persona Table

| # | Name | Occupation | Conversational Style | Daily Life Detail (`{day_detail}`) | Loved One (`{loved_one}`, `{relation}`) |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **1** | **Alex** | Baker | Warm, talkative, tells little anecdotes | Your new rye loaf sold out before 9 am | Dana (older sibling) |
| **2** | **Sam** | Upholsterer | Easygoing, practical, short sentences | You finished re-covering a customer's armchair | Robin (cousin) |
| **3** | **Jordan** | Librarian | Soft-spoken, a little formal | Someone returned a book three years overdue | Kerry (college roommate) |
| **4** | **Casey** | Gardener | Calm, patient, plain-spoken | You fixed the leaking hose at the community garden | Jesse (younger sibling) |
| **5** | **Riley** | Swim coach | Expressive and animated | Two kids in your class passed their first swim test | Charlie (godparent) |
| **6** | **Taylor** | Pharmacy assistant | Measured, unhurried | The shop's card machine was down all morning | Frankie (childhood friend) |
| **7** | **Morgan** | Carpenter | Direct, dry sense of humor | You finished a bookshelf for a neighbor | Lee (older sibling) |
| **8** | **Jamie** | Barista | Friendly, fast-talking | You trained a new coworker on the espresso machine | Skyler (cousin) |
| **9** | **Quinn** | Tailor | Matter-of-fact, wry | A customer dropped off three suits to hem | Reese (school friend) |
| **10** | **Avery** | Bookkeeper | Orderly, literal | You finished a client's quarterly accounts a day early | Pat (younger sibling) |
| **11** | **Rowan** | Dog groomer | Gentle and reassuring | A nervous poodle finally sat still for a full trim | Drew (college friend) |
| **12** | **Sage** | Florist | Cheerful and upbeat | A wedding order of 200 tulips arrived on time | Kendall (cousin) |
| **13** | **Emerson** | Hardware clerk | Friendly, slow-paced, folksy sayings | You spent the morning restocking paint | Ellis (older sibling) |
| **14** | **Parker** | Dry-cleaner clerk | Polite, laughs easily | A customer left a suit unclaimed for a month | Marley (cousin) |

---

## 4. Persona Design Principles (Guarding Against Confounds)

To guarantee that persona profiles never interfere with the 6 experimental factors, every persona adheres to 5 strict methodological constraints:

1. **Strict Independence from Experimental Knobs:**  
   Persona rows define character background only. They contain **zero information** about authority, closeness, wealth, age, or reliability. Experimental knobs are injected solely through standardized knob templates.
2. **Gender-Neutral Names:**  
   Every name (Alex, Sam, Jordan, etc.) is traditionally gender-neutral. The agent's actual perceived gender is injected dynamically per run via the Gender knob (`man` vs. `woman`).
3. **Mid-Status, Non-Clashing Occupations:**  
   All occupations sit in the middle of socio-economic status (baker, tailor, carpenter). 
   * *Institutional roles are forbidden:* No mayors, judges, police, bankers, or unemployed residents.
   * *Free-travel roles are forbidden:* Sam was originally drafted as a bus driver, and Quinn as a postal worker. Both were replaced (upholsterer and tailor) because a bus driver rides the bus for free, and a postal worker walks the entire town, which would undercut the $5 bus fee.
   * *Topical conflict is forbidden:* Riley was originally a music teacher; this was swapped to swim coach to prevent occupational bias toward concerts.
4. **Tonal-Only Conversational Styles:**  
   Styles describe pacing and warmth (e.g., *"warm, tells little anecdotes"*, *"measured, unhurried"*). Styles **never describe credulity or skepticism** (e.g., traits like *"skeptical"*, *"inquisitive"*, or *"gullible"* are strictly forbidden).
5. **Daily Life Details & Out-of-Town Loved Ones:**  
   * Each persona has an ordinary daily work event (e.g., rye loaf sold out, fixed a garden hose). This gives the agent ordinary personal news to discuss with their loved one, ensuring that `NOT_MENTIONED` is an authentic, unforced choice.
   * Every loved one lives out of town and has no personal stake in Alder Creek events.

---

## 5. Mathematical Seating & Layer Rotation Architecture

Every town has **13 fixed seats**:
* **Seat 0:** The Source Agent.
* **Seats 1 to 6 (Layer 1):** The 6 First-Hand Listeners who attend morning coffee at the café.
* **Seats 7 to 12 (Layer 2):** The 6 Second-Hand Listeners who miss morning coffee and hear news in the afternoon.

```
                      ┌────────────────────────┐
                      │  SEAT 0: SOURCE AGENT  │
                      └───────────┬────────────┘
                                  │ (Café Departure Broadcast)
                                  ▼
      ┌────────────────────────────────────────────────────────┐
      │          LAYER 1: FIRST-HAND LISTENERS (CAFÉ)          │
      │   Seat 1    Seat 2    Seat 3    Seat 4    Seat 5    Seat 6 │
      └─────┬─────────┬─────────┬─────────┬─────────┬─────────┬────┘
            │         │         │         │         │         │ (Afternoon Catch-Up)
            ▼         ▼         ▼         ▼         ▼         ▼
      ┌─────┴─────────┴─────────┴─────────┴─────────┴─────────┴────┐
      │         LAYER 2: SECOND-HAND LISTENERS (CATCH-UP)       │
      │   Seat 7    Seat 8    Seat 9   Seat 10   Seat 11   Seat 12 │
      └────────────────────────────────────────────────────────┘
```

### The 13-Seed Latin Square Rotation:
To eliminate position and persona bias, the code shifts the 13 personas through the 13 seats across the 13 seeds of each cell:
* **Seed 0:** Persona 0 is Source; Personas 1–6 are Layer 1; Personas 7–12 are Layer 2.
* **Seed 1:** Persona 12 is Source; Personas 0–5 are Layer 1; Personas 6–11 are Layer 2.
* ...up to **Seed 12**.

#### Mathematical Symmetry:
Across the 13 seeds, **every single persona**:
* Sits in Seat 0 (Source) exactly **1 time** ($1/13$).
* Sits in Layer 1 (Café First-Hand) exactly **6 times** ($6/13$).
* Sits in Layer 2 (Catch-Up Second-Hand) exactly **6 times** ($6/13$).

No character is permanently an authority, a source, or a passive listener.

---

## 6. Constant Dyadic Pairing ($\text{Seat } i \longleftrightarrow \text{Seat } i + 6$)

In Scene 3, each First-Hand Listener meets exactly one Second-Hand Listener for afternoon catch-up.

To guarantee that the Rumor Run and its matched Truth Twin can be compared with zero confounding noise:
1. **Seat Matching is Fixed and Constant:**  
   $$\text{Seat } i \longleftrightarrow \text{Seat } (i + 6)$$
   * Seat 1 pairs with Seat 7
   * Seat 2 pairs with Seat 8
   * Seat 3 pairs with Seat 9
   * Seat 4 pairs with Seat 10
   * Seat 5 pairs with Seat 11
   * Seat 6 pairs with Seat 12
2. **Twin Identity:**  
   Because a Rumor run and its matched Truth Twin share the **exact same seed**, they get the **exact same persona pairings**. If Alex (Seat 1) meets Sam (Seat 7) in the rumor run, Alex meets Sam in the truth twin. Any difference in rumor transmission is mathematically attributable strictly to the truth value of the claim.

---

## 7. Persona #14 (Parker) in Two-Source Probes

In Probes 1 & 2, there are **2 Sources** in town. 

### Preservation of the 6 Catch-Up Pairs:
To keep the afternoon catch-up structure identical across all modules:
* Probes contain strictly **14 agents**: **2 Sources** + **12 Listeners (6 First-Hand, 6 Second-Hand)**.
* The 12 listeners form the exact same 6 pairs as the main experiment.

### Eliminating Persona Bias for the Second Source:
* Source 1 is drawn from the standard 13 Latin Square personas.
* Source 2 uses **Persona #14 (Parker, dry-cleaner clerk)**.
* **The 50/50 Swap Rule:**  
  To ensure Parker's polite, laughing personality never gives one source an unfair believability advantage:
  * In 50% of probe runs: **Source 1 is Parker**, and Source 2 is the Latin Square persona.
  * In the other 50% of probe runs: **Source 2 is Parker**, and Source 1 is the Latin Square persona.
  * *Result:* Persona personality effects between the two conflicting sources cancel out to zero.
