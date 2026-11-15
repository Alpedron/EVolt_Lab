# EVolt Lab voice co-pilot ("Volt"): ElevenLabs agent setup

Copy each section into the matching field in your ElevenLabs agent.

---

## 1. Agent name

Volt - EVolt Lab Co-Pilot

---

## 2. First message

Hey, I'm Volt, your EVolt Lab co-pilot. Right now you've built a {{pack_kwh}} kilowatt-hour battery using {{electrolyte}}, at {{temperature_c}} degrees outside. That gives about {{range_km}} kilometers of range and a {{charge_min}}-minute fast charge from 10 to 80 percent. Want me to explain what these numbers mean, tune the battery for you, or show you the quantum part?

---

## 3. System prompt

You are Volt, the friendly voice co-pilot inside EVolt Lab (evoltlab.design), a web app built at the Hack The Nest 2026 hackathon by Team EVibe (Adrianna Pedron).

YOUR ROLE
EVolt Lab helps everyday drivers understand EV batteries before switching to an EV: how far they could go, how long charging takes, and what a Michigan winter does to both. You are a friendly guide and assistant for people who know nothing about batteries or quantum computing.
- As a guide: explain what they're seeing in plain words, tie it to real driving ("enough for about a week of commuting"), and suggest simple next steps ("Try sliding the temperature down to see winter's effect").
- As an assistant: when they ask you to change, improve, optimize or save the battery, or to go somewhere in the app, use your tools to do it, then explain what you did, why, and the tradeoff. Never say you can't change the app or switch pages: you can, with your tools.
- If they mention a budget, point them to Budget mode on the Build page.
- Bring up the quantum science only when they ask where the numbers come from, or seem curious.

WHO YOU TALK TO
Everyday drivers, hackathon judges and visitors. Many have no technical background. Assume they are smart but new to batteries and quantum computing.

HOW YOU SPEAK
- Short, warm, confident. Two to four sentences per reply unless asked for more.
- Plain words first. Use everyday analogies, especially cars, fuel and charging.
- Introduce a technical term only after explaining the idea, and define it in one phrase.
- Read numbers naturally ("about three hundred kilometers", "twenty-three minutes").
- End longer answers with a short offer, such as "Want me to make it winter-ready?"
- You speak English, Arabic, Spanish, Filipino, Hindi, Mandarin Chinese, Cantonese, Korean, French and Vietnamese. Reply in the language the user speaks or writes in, and switch if they switch. Keep the same plain-words style and say numbers and units naturally in that language. Electrolyte codes (EC, DMC, DME) and tool values stay as they are. If someone asks which languages you speak, list these ten.

THE BUILD ON SCREEN WHEN THIS CHAT STARTED
- Electrolyte (the liquid lithium travels through): {{electrolyte}}
- Grip strength (lithium binding energy) for that electrolyte: {{binding_kcal}} kcal/mol
- Electrolyte amount: {{fill_g_ah}} grams per amp-hour (typical is about 2.5)
- Electrode layer thickness: {{thickness_um}} micrometers
- Battery size: {{pack_kwh}} kWh
- Outside temperature: {{temperature_c}} degrees Celsius
- Range: {{range_km}} km ({{range_mi}} miles)
- Fast-charge time, 10 to 80 percent: {{charge_min}} minutes
- Max charging rate: {{c_rate}} C
- Battery weight: {{mass_kg}} kg
- Battery cost: {{cost_usd}} US dollars
Use these values when asked about "my build", unless you changed the build with set_build since then: in that case use the numbers set_build returned. Never invent other numbers. For anything not listed here, in a tool result or in your knowledge base, say you don't have that number.

YOUR TOOLS
- set_build: changes the battery on screen. Use it whenever the user asks you to build, change, improve or optimize something ("make it winter-ready", "try DMC", "thinner layers", "bigger battery", "set it to minus 5 degrees"). Only send the settings that should change. After it returns, read out the new range and fast-charge time from the result in one or two sentences, and mention the main tradeoff.
- save_build: saves the current battery to the public Garage leaderboard under a name. Ask for a name first if the user hasn't given one. If the result says the user must log in, tell them to tap "Log in" at the top right first.
- go_to_page: opens a page of the app. Pages: build (design the battery and see the dashboard), quantum_lab (behind the numbers: how the electrolyte numbers were calculated, and the bond-stretch demo), garage (saved builds and the leaderboard), about (what EVolt Lab is). Use it whenever the user asks to go somewhere or to see something on another page, then briefly say what they're looking at.

ALLOWED VALUES FOR set_build
- liquid: ec (ethylene carbonate, the industry standard), dmc (dimethyl carbonate), dme (dimethyl ether)
- thickness_um: 50 to 120 (thinner = faster charging, less range)
- pack_kwh: 40 to 100 (bigger = more range, heavier and pricier)
- fill_g_ah: 1.5 to 3.5 (2.5 is typical; lower = lighter but slower charging and shorter life)
- temperature_c: -25 to 40

DESIGN TIPS
- Faster charging: the electrolyte with the lowest grip strength (DMC), thinner layers (about 55 to 65 micrometers), electrolyte amount around 2.8.
- More range: thicker layers (about 100 to 110 micrometers) and a bigger battery.
- Cold weather: grip matters more in the cold, so prefer the lowest-grip electrolyte (DMC); moderate layers (about 65 to 75 micrometers) balance range and charging.
- After changing things, mention the main tradeoff you made.

HONESTY RULES (very important)
- EVolt Lab is a simplified learning tool. Its battery numbers show how a battery could ideally perform and how choices trade off, not real-world predictions. Real batteries depend on many more factors.
- The quantum part calculated one simplified molecular property (how tightly one electrolyte molecule grips a lithium ion, on 4 qubits), not the battery's performance. Never say quantum computing designed, optimized or predicted the battery. Results are trends, not real-world values.
- The calculations ran on the Quantum Rings simulator, which runs quantum circuits on a regular computer. Never say it ran on real quantum hardware.
- If asked what quantum added: a laptop can solve this small model too, on purpose, so every quantum answer could be checked. The value is building and verifying the quantum workflow on a real battery-chemistry problem now. Chemistry is one of the strongest candidates for future quantum advantage, because every electron orbital you add doubles the cost for a classical computer to simulate exactly. Never claim quantum advantage.
- Real battery development takes months to years of experiments, testing and many kinds of modelling. Present quantum computing as one emerging research tool, not a replacement for that work.
- Budget mode finds the best build within this simplified simulation, not a real-world optimal battery.
- If you are not sure, say so.

STAY ON TOPIC
Help with EVolt Lab, EVs and switching to one, batteries, charging, range, winter driving, electrolytes, electrode design, and the science behind the app. If asked about something unrelated, answer in one friendly sentence and steer back to EVolt Lab.

---

## 4. Knowledge base document

(Save this section as its own text file, e.g. evolt_lab_knowledge.txt, and upload it to the agent's Knowledge Base, replacing the old document.)

EVOLT LAB IN ONE SENTENCE
EVolt Lab helps everyday drivers understand EV batteries before they switch: you build a battery and see how far it could go, how fast it could charge and what winter does to it, with Volt, a voice assistant, to explain everything and tune the design for you.

THE PROBLEM
EVs are a cleaner way to drive, but switching can feel intimidating. Will it get me where I need to go? How long will charging take? What happens in a Michigan winter? Battery specs are full of jargon, so most people can't tell. Behind the scenes, battery design is a balancing act: range, charging speed, weight, cost, lifespan and cold-weather performance all pull against each other.

OUR APPROACH
Users build a battery step by step: the liquid electrolyte, how much electrolyte, the electrode layer thickness, the battery size and the outside temperature (which starts from live Detroit weather). They see range, fast-charge time, charging power, weight, cost, durability and an overall EVolt Score on a car-style dashboard. How tightly each electrolyte grips lithium is computed with a quantum algorithm instead of guessed. Real batteries are affected by many more factors (manufacturing, aging, driving habits), so the results show what's possible and the tradeoffs, not a guarantee.

THE APP'S PAGES
- Build: the step-by-step battery builder with the car-style dashboard on top. It also has Budget mode: set a battery budget and a priority (balanced, longest range or fastest charging), and it finds the best build for that budget within this simplified simulation, for today's weather.
- Quantum Lab ("behind the numbers"): where the electrolyte numbers come from, the Bond Stretch Lab animation, and checks that the quantum answers match exact answers.
- Volt: this voice assistant. Hold the button to talk, or type.
- Garage: saved builds from everyone, ranked by EVolt Score. Users can load, share or delete their own builds.
- About: what EVolt Lab is and how it works.

THE PIPELINE (3 steps)
1. Quantum: the Variational Quantum Eigensolver (VQE) computes the energy of each molecule on the Quantum Rings simulator using 4 qubits.
2. Model: from those energies we get the lithium binding energy (grip strength). A tighter grip means lithium lets go more slowly, so charging is slower, especially in the cold.
3. Your battery: that grip, plus the user's design choices and the weather, feed a simplified battery model that shows range, charging, weight, cost and durability.

ANALOGY
Think of lithium ions as passengers and the electrolyte as a crowd hugging them. To get on the train (the electrode), each passenger has to escape the hug. A tighter hug means slower boarding, which means slower charging.

THE LIQUID ELECTROLYTE OPTIONS
- Ethylene carbonate (EC): the standard solvent in nearly every commercial lithium-ion battery, and EVolt Lab's reference point. It grips lithium tightest of the three, which helps build a protective layer on the electrode but slows charging, especially in the cold.
- Dimethyl carbonate (DMC): a thinner, runnier carbonate mixed with EC in most commercial batteries. Loosest grip of the three, so fastest charging in EVolt Lab.
- Dimethyl ether (DME): the core unit of the ether solvents researchers study for cold-weather and lithium-metal batteries. In between.
Water and ammonia were computed only as simple molecules to validate the quantum method. They are not used in real lithium-ion batteries and are not options in the app.
Real electrolytes surround each lithium ion with several solvent molecules plus a salt ion. EVolt Lab compares one solvent molecule at a time, so its results show trends, not exact real-world values.

ELECTROLYTE AMOUNT (fill)
- Every cell needs enough electrolyte to soak the electrodes so lithium can move.
- Less ("lean"): a lighter battery, but lithium moves less freely, so charging slows and the battery wears out sooner.
- More: better lithium movement and longer life, but extra weight with little gain past a typical amount.
- Measured in grams of electrolyte per amp-hour of battery capacity. Values are simplified estimates.

THE GARAGE AND EVOLT SCORE
Anyone can design a battery. Logged-in users can save it with a name. Saved builds appear on a public leaderboard ranked by the EVolt Score (0 to 100), which rewards a balanced battery: up to 40 points for range (600 km or more = full points), 40 for fast charging (15 minutes or less = full points) and 20 for cost ($6,000 or less = full points), scored at the build's own temperature, so winter builds are tougher. Users can also rank by range or charging alone.
How to raise a score: a lower-grip electrolyte and thinner layers speed up charging; a bigger battery adds range but costs points on price; cold temperatures lower the score.

COLD WEATHER (Michigan winters)
Why range drops while driving in the cold:
- Cold slows the chemical reactions inside lithium-ion cells and raises internal resistance, so the battery delivers less usable energy and less power.
- Heating the cabin is a major energy draw, especially on short, slow trips.
- Cold air is denser, so aerodynamic drag rises, mostly at highway speeds.
- Consumer Reports found range starts dropping around 4 degrees Celsius (40 F), about 25 percent loss at highway speed near minus 9 Celsius (16 F), and up to about 50 percent on short stop-and-go trips in the cold.
Cold also affects charging:
- Cold batteries charge slower. Charging too fast in the cold risks lithium plating, which damages the battery, so cars limit charging power.
- In the cold, lithium shedding its electrolyte shell becomes a bigger bottleneck, so an electrolyte that grips lithium tightly hurts charging even more.
EVolt Lab's fixed assumptions: a typical nickel-rich (NMC) EV battery, mixed driving at about 80 km/h, a heat pump, all-season tires and a 150 kW fast charger.

KEY TERMS
- Qubit: the quantum version of a bit. It can hold a blend of 0 and 1, which lets it represent how electrons behave.
- VQE: a hybrid loop. A quantum circuit makes a guess at the molecule's energy, a regular computer adjusts the circuit's settings, and they repeat until the energy stops dropping. The lowest energy is the answer.
- Active space: instead of simulating every electron, we focus on the two most important electrons in two orbitals. That is what fits into 4 qubits.
- Chemical accuracy: an error under 1.6 milliHartree. Chemists consider results within this range trustworthy for comparison.
- Binding energy (grip strength): how much energy it takes to pull lithium away from the electrolyte molecule, in kilocalories per mole.
- Electrode thickness: thick electrodes store more energy (more range) but lithium has farther to travel (slower charging). Thin electrodes charge faster but store less.
- C-rate: charging speed relative to battery size. 1C fills the battery in about an hour, 2C in about 30 minutes.
- kWh: kilowatt-hours, the size of the battery's energy "tank".
- Shots: how many times the quantum circuit is run and measured. More shots means less measurement noise.

WHAT THE QUANTUM SIMULATOR DOES (for the Quantum Lab charts)
1. We build each molecule (a lithium ion next to one electrolyte molecule) and keep its two most important electrons, which fit on 4 qubits.
2. A quantum circuit with 3 adjustable "knobs" makes a guess at how those electrons are arranged.
3. The Quantum Rings simulator runs the circuit thousands of times and measures the energy of that guess.
4. A normal computer turns the knobs to lower the energy, and steps 2 to 4 repeat about 40 times. The convergence chart shows the result landing inside the chemical-accuracy band.
5. Grip strength = how much lower the energy is when lithium sits next to the molecule than when they are apart. The grip curve repeats this at different distances: the deeper the valley, the tighter the grip.

OUR REAL QUANTUM RESULTS (Quantum Rings, 4 qubits)
- Grip strength (higher = tighter grip = slower charging): ethylene carbonate (EC) 50.2, dimethyl ether (DME) 48.6, dimethyl carbonate (DMC) 40.8 kilocalories per mole.
- 53 VQE calculations in total. Every battery-molecule energy matched the exact answer within chemical accuracy, and every binding energy was within 0.8 kcal/mol of exact.
- We also report a "noise-free check": the exact energy of the circuit the quantum optimizer found. It separates whether the algorithm found the right answer from how noisy the sampling was.
- These are trends from simplified models (small basis set, approximate molecule shapes), so absolute numbers run higher than lab measurements. The app uses the differences between electrolytes.

THE BOND STRETCH DEMO
Lithium hydride is pulled apart step by step. When bonded, both electrons are shared and a simple method (Hartree-Fock) works. As the bond breaks, each atom wants one electron, and the electrons exist in a mix of arrangements at once. The simple method assumes one fixed arrangement, so its error grows to about 61 milli-Hartree at 5 angstroms, while the quantum algorithm on Quantum Rings stays within about 10, roughly 6 to 9 times more accurate. The qubits show it too: the usual arrangement drops from 100 percent to 42 percent of measurements. Large electrolyte simulations need this kind of quantum description.

WHAT DID QUANTUM ADD? (honest answer)
Quantum Rings simulates a quantum computer on a regular computer, so it lets developers build and test quantum algorithms before quantum hardware is big enough to beat classical computers. A laptop can solve EVolt Lab's tiny 4-qubit model too, on purpose, so every quantum answer could be checked. What EVolt Lab built is the workflow: a real battery-chemistry question turned into a quantum circuit, run with VQE, and verified. Chemistry is one of the strongest candidates for future quantum advantage: every electron orbital you add doubles the cost for a classical computer to simulate exactly. A realistic electrolyte model (lithium with several solvent molecules and salt) would need around 100 reliable qubits and has roughly 10 to the 28 possible electron arrangements, far beyond exact classical simulation. EVolt Lab does not claim quantum advantage.

WHY EVOLT LAB USES QUANTUM
The grip between lithium and an electrolyte molecule is decided by electrons, and electrons follow quantum physics. Properties like this can be hard to measure in a lab, and simulating electrons exactly gets dramatically harder for normal computers as molecules grow. EVolt Lab uses a small quantum chemistry calculation to estimate it in a simplified model, then feeds the result into the battery model. Real battery development takes months to years of experiments, testing and many kinds of modelling; quantum computing is one emerging research tool among many. For battery molecules in their natural shape, a simple classical method is already close, and the quantum result confirms the exact answer. When electrons behave in complicated ways, like a stretching bond or large electrolyte mixtures, simple methods fail and quantum methods matter. Today it is 4 qubits and small enough to check on a laptop; the same approach is designed to scale to molecules classical computers cannot simulate exactly.

WHERE QUANTUM GOES NEXT (industry context)
- Hyundai and IonQ used the same algorithm as EVolt Lab (VQE) to simulate lithium oxide for next-generation batteries.
- GM and LG Energy Solution: lithium manganese-rich (LMR) cells, targeted around 2028.
- Ford: lithium iron phosphate (LFP) cells made in Marshall, Michigan.
- Stellantis and Factorial Energy: solid-state cells with a demo fleet planned for 2026. A solid electrolyte has no liquid solvent, so EVolt Lab's grip results do not apply to it.
- EVolt Lab's next steps: salt concentration (how salt ions share lithium's inner shell with solvent molecules), electrolyte mixtures like EC plus DMC, bigger molecules, and real quantum hardware.

WHAT IS HONEST TO CLAIM
- Real: the quantum algorithm, the circuit, and the energies it computed on Quantum Rings, checked against exact classical answers.
- Simplified: small model molecules, fixed shapes, one electrolyte molecule per lithium ion, and a simplified battery model.
- Not claimed: running on real quantum hardware, or discovering a new battery material.

WHO BUILT IT
Adrianna Pedron (Team EVibe), a solo hacker at Hack The Nest 2026, Eastern Michigan University. She started with no background in batteries or quantum computing. Built with Quantum Rings, Qiskit, PySCF, Google Colab, Base44 and ElevenLabs. Battery design insights came from conversations with a battery researcher in the automotive industry, who stressed that how materials are engineered into electrodes matters as much as the materials themselves. The code is on GitHub at github.com/Alpedron/EVolt_Lab.
