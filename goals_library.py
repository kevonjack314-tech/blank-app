"""Library of self-improvement areas.

Each area has an ordered ladder of levels, easiest first. Every level holds a
few task variants so day-to-day tasks don't repeat word for word. The app maps
your timeline onto the ladder: a short deadline climbs levels quickly, a long
one lingers on each level so the steps stay tiny.
"""

GOAL_LIBRARY = {
    "social_anxiety": {
        "name": "Overcome Social Anxiety",
        "emoji": "🫂",
        "description": "Tiny daily exposures that make social situations feel less scary over time.",
        "support_note": None,
        "levels": [
            {
                "title": "Warming up alone",
                "tasks": [
                    "Write down one social situation that makes you anxious and rate the fear 1-10. Just naming it counts.",
                    "Practice saying 'Hi, how's it going?' out loud to yourself 5 times in a relaxed tone.",
                    "Spend 5 minutes people-watching somewhere public (a window counts). Notice nobody is watching you back.",
                ],
            },
            {
                "title": "Micro-contact",
                "tasks": [
                    "Make eye contact and nod or smile at one stranger today.",
                    "Say 'good morning' or 'hey' to one person you pass today.",
                    "Hold the door for someone and say 'no problem' if they thank you.",
                ],
            },
            {
                "title": "Short exchanges",
                "tasks": [
                    "Ask a store employee where something is, even if you already know.",
                    "Give one genuine compliment to someone today ('I like your shoes' is plenty).",
                    "Order food or coffee in person and add one extra sentence, like asking what they recommend.",
                ],
            },
            {
                "title": "Small talk reps",
                "tasks": [
                    "Start a 30-second small-talk exchange with a coworker, classmate, or neighbor (weather, weekend, anything).",
                    "Ask someone one open question about themselves and listen to the full answer.",
                    "Make a lighthearted comment out loud in a group setting, even a small one.",
                ],
            },
            {
                "title": "Holding conversations",
                "tasks": [
                    "Keep one conversation going for 2+ minutes by asking follow-up questions.",
                    "Share one small personal opinion in a conversation instead of just agreeing.",
                    "Call (don't text) someone to ask or arrange something.",
                ],
            },
            {
                "title": "Being seen",
                "tasks": [
                    "Speak up once in a meeting, class, or group chat with a question or comment.",
                    "Eat or have a coffee alone in public without hiding behind your phone for 10 minutes.",
                    "Tell someone about something you did recently, without downplaying it.",
                ],
            },
            {
                "title": "Social initiative",
                "tasks": [
                    "Invite someone to hang out, grab lunch, or join you for something specific.",
                    "Join a conversation that's already happening instead of waiting to be pulled in.",
                    "Introduce yourself to one new person by name.",
                ],
            },
            {
                "title": "Comfort in the deep end",
                "tasks": [
                    "Attend a social event or group activity and stay at least 30 minutes.",
                    "Tell a short story to a group of 2+ people.",
                    "Do something mildly embarrassing on purpose (ask a silly question, sing a line out loud) and notice that you survive it just fine.",
                ],
            },
        ],
    },
    "communication": {
        "name": "Communicate Better",
        "emoji": "🗣️",
        "description": "Daily reps in listening, clarity, and saying what you actually mean.",
        "support_note": None,
        "levels": [
            {
                "title": "Noticing your patterns",
                "tasks": [
                    "In one conversation today, count how many times you interrupt. Just observe, don't judge.",
                    "After a conversation, jot one sentence: did you say what you actually meant?",
                    "Notice one moment today where you stayed quiet but wanted to say something. Write down what it was.",
                ],
            },
            {
                "title": "Listening first",
                "tasks": [
                    "In one conversation, let the other person completely finish before you respond. Every time.",
                    "Ask one follow-up question before sharing your own take.",
                    "Put your phone face-down and out of reach during one full conversation.",
                ],
            },
            {
                "title": "Reflecting back",
                "tasks": [
                    "Once today, repeat back what someone said in your own words: 'So you're saying...' and let them confirm.",
                    "Ask someone 'what do you mean by that?' instead of assuming, once today.",
                    "Name the emotion you hear once today: 'sounds like that was frustrating.'",
                ],
            },
            {
                "title": "Speaking clearly",
                "tasks": [
                    "Before one important message or conversation today, write the one-sentence version of your point first. Lead with it.",
                    "Replace one vague answer ('whatever works') with a real preference today.",
                    "Cut filler: in one conversation, pause silently instead of saying 'um' or 'like'.",
                ],
            },
            {
                "title": "Saying the hard part",
                "tasks": [
                    "Say 'no' to one small thing today without over-explaining.",
                    "Use an 'I' statement for one thing that's bothering you: 'I feel X when Y.'",
                    "Ask directly for one thing you'd normally hint at.",
                ],
            },
            {
                "title": "Handling friction",
                "tasks": [
                    "In one disagreement (even tiny), state the other person's view fairly before giving yours.",
                    "When criticized or corrected today, say 'let me think about that' instead of defending instantly.",
                    "Bring up one small unresolved thing with someone, calmly, before it grows.",
                ],
            },
            {
                "title": "Advanced reps",
                "tasks": [
                    "Have one conversation where your only goal is to make the other person feel fully heard.",
                    "Give someone specific, honest positive feedback (not just 'good job' — say what exactly was good).",
                    "Lead a discussion, meeting, or group decision today, keeping everyone involved.",
                ],
            },
        ],
    },
    "self_doubt": {
        "name": "Beat Self-Doubt",
        "emoji": "💪",
        "description": "Build real confidence with small daily proof that you can trust yourself.",
        "support_note": None,
        "levels": [
            {
                "title": "Catching the voice",
                "tasks": [
                    "Write down one self-doubting thought you had today, word for word. Just catch it.",
                    "Count how many times today you say 'sorry' or 'I might be wrong' when you didn't need to.",
                    "Write down one thing you did OK today. Not great — just OK. That counts.",
                ],
            },
            {
                "title": "Talking back",
                "tasks": [
                    "Take one doubting thought and write the evidence for and against it, like a lawyer.",
                    "Rewrite one 'I can't...' thought from today as 'I haven't yet...'",
                    "Ask: 'would I say this to a friend?' about one self-critical thought. If not, rewrite it kinder.",
                ],
            },
            {
                "title": "Small proof",
                "tasks": [
                    "Make one small decision today in under 60 seconds and don't second-guess it afterward.",
                    "Do one small thing you've been putting off because you 'might mess it up'.",
                    "Write down 3 past moments where you handled something you doubted you could.",
                ],
            },
            {
                "title": "Owning your voice",
                "tasks": [
                    "Give one opinion today without softening it ('maybe', 'I guess', 'this is probably dumb but...').",
                    "Accept one compliment with just 'thank you' — no deflecting.",
                    "Share one idea at work, school, or with friends before you feel 100% sure about it.",
                ],
            },
            {
                "title": "Acting despite doubt",
                "tasks": [
                    "Do one thing today at 70% ready instead of waiting to feel 100% ready.",
                    "Volunteer for one small thing you'd normally let someone else take.",
                    "Set one small boundary today, even if your gut says 'don't make a fuss'.",
                ],
            },
            {
                "title": "Bigger swings",
                "tasks": [
                    "Ask for something where the answer might be no (a favor, a discount, an opportunity).",
                    "Show someone a piece of your work and ask what they honestly think.",
                    "Commit publicly (tell one person) to a goal you've kept private out of fear of failing.",
                ],
            },
            {
                "title": "Self-trust on autopilot",
                "tasks": [
                    "Take on one challenge today that past-you would have talked yourself out of.",
                    "Teach or help someone with something you know — notice that you do know it.",
                    "Write a short letter from future confident you to present you. Keep it.",
                ],
            },
        ],
    },
    "addiction_recovery": {
        "name": "Substance Recovery",
        "emoji": "🌱",
        "description": "Gentle daily steps to reduce dependence and build a life that doesn't need the substance.",
        "support_note": (
            "This app is a companion, not treatment. Quitting some substances abruptly can be "
            "medically dangerous — please involve a doctor, and consider support like SAMHSA's free "
            "helpline (1-800-662-4357 in the US) or a local recovery group. You deserve real support."
        ),
        "levels": [
            {
                "title": "Honest snapshot",
                "tasks": [
                    "Write down, just for you, how much/how often you used this week. No judgment — just the truth on paper.",
                    "Write one sentence about why you want this to change. Keep it somewhere you'll see it.",
                    "Note your top 3 trigger moments (times, places, feelings, people) when cravings hit hardest.",
                ],
            },
            {
                "title": "Tiny friction",
                "tasks": [
                    "Add one obstacle between you and using today (move it out of sight, don't carry cash, take a different route).",
                    "Delay one urge by 10 minutes today. Set a timer. You can decide after it rings.",
                    "Tell one safe person that you're working on cutting back. Just one.",
                ],
            },
            {
                "title": "Swaps and delays",
                "tasks": [
                    "When a craving hits today, do a 5-minute replacement first: walk, cold water on your face, 10 pushups, or call someone.",
                    "Push your first use of the day later by 30+ minutes than usual.",
                    "Prepare a 'craving kit' for tomorrow: gum, a snack, headphones, a person to text.",
                ],
            },
            {
                "title": "Shrinking the habit",
                "tasks": [
                    "Skip one usual using-occasion completely today, using your replacement plan.",
                    "Avoid one trigger location or situation entirely today.",
                    "Track every craving today: time, trigger, intensity 1-10, what you did. Knowledge is power.",
                ],
            },
            {
                "title": "Building support",
                "tasks": [
                    "Look up one support option today (a meeting, an online group, a counselor) — just find the info.",
                    "Attend or join one support meeting/group/call, in person or online.",
                    "Ask one person to be your check-in contact and agree on how often you'll text them.",
                ],
            },
            {
                "title": "Clean stretches",
                "tasks": [
                    "Aim for a fully clean day today. If a slip happens, write down what led to it — data, not failure.",
                    "Plan tonight's high-risk hours in advance: where you'll be, who with, doing what.",
                    "Do one activity you used to love before the substance took space. Even 20 minutes.",
                ],
            },
            {
                "title": "New identity",
                "tasks": [
                    "Write about who you are without it — what mornings, money, and relationships look like.",
                    "Make one concrete plan for the money/time you're saving (calculate it — it adds up fast).",
                    "Reach out to someone else who's struggling or in recovery. Helping others helps you stay strong.",
                ],
            },
        ],
    },
    "relationship": {
        "name": "Healthier Relationship",
        "emoji": "❤️",
        "description": "Daily actions for loyalty, trust, and being a better partner.",
        "support_note": None,
        "levels": [
            {
                "title": "Looking inward",
                "tasks": [
                    "Write down one pattern of yours that hurts the relationship (going quiet, snapping, wandering attention). Naming it is step one.",
                    "List 3 things you genuinely appreciate about your partner. Details, not generalities.",
                    "Notice one moment today where you chose your phone/distraction over your partner. Just notice.",
                ],
            },
            {
                "title": "Small deposits",
                "tasks": [
                    "Give your partner one specific compliment today about who they are, not what they did for you.",
                    "Do one small unasked-for act of care today (their coffee, their chore, a checking-in text).",
                    "Put your phone away completely for 15 minutes of undivided attention with them.",
                ],
            },
            {
                "title": "Real conversations",
                "tasks": [
                    "Ask your partner one question about their inner world today (a hope, a stress, a memory) and just listen.",
                    "Share one thing you felt today — actually name the feeling — instead of just reporting events.",
                    "Ask: 'Is there anything I could do this week that would make you feel more loved?' Then do it.",
                ],
            },
            {
                "title": "Guarding the boundaries",
                "tasks": [
                    "Identify one 'gray area' behavior you'd hide from your partner if they saw it. Decide today to drop it.",
                    "Unfollow, mute, or distance yourself from one temptation source (a person, an app, a habit).",
                    "When attraction or temptation shows up today, redirect the energy: send your partner a flirty or loving message instead.",
                ],
            },
            {
                "title": "Repair skills",
                "tasks": [
                    "Apologize for one thing — cleanly, no 'but'. Name what you did and what you'll do differently.",
                    "In one tense moment today, take a 10-minute break instead of escalating, and come back to finish calmly.",
                    "Bring up one small resentment gently before it turns into a big one: 'Hey, can we talk about...'",
                ],
            },
            {
                "title": "Rebuilding trust",
                "tasks": [
                    "Be proactively transparent about one thing today (plans, money, who you were with) before being asked.",
                    "Keep every promise you make today, even tiny ones. If you can't keep it, don't make it.",
                    "Ask your partner: 'What helps you feel secure with me?' and listen without defending.",
                ],
            },
            {
                "title": "Deep partnership",
                "tasks": [
                    "Plan a real date — you handle everything, tailored to what they love.",
                    "Write your partner a short letter about your commitment and one thing you're working on for them.",
                    "Have the 'state of us' talk: what's going well, what needs work, one goal together.",
                ],
            },
        ],
    },
    "reading": {
        "name": "Read More",
        "emoji": "📚",
        "description": "From 'I never read' to a steady reading habit, a few pages at a time.",
        "support_note": None,
        "levels": [
            {
                "title": "Set the stage",
                "tasks": [
                    "Pick the book you'll start with and put it somewhere you'll physically see it daily.",
                    "Decide your reading spot and time (e.g., bed at 10pm, couch after dinner). Write it down.",
                    "Delete or log out of one time-sink app, or move it off your home screen, to make room for reading.",
                ],
            },
            {
                "title": "First pages",
                "tasks": [
                    "Read just 2 pages today. You're allowed to stop after — the win is starting.",
                    "Read for 5 minutes with your phone in another room.",
                    "Read 2 pages and underline or note one line you liked.",
                ],
            },
            {
                "title": "Building the streak",
                "tasks": [
                    "Read 10 minutes today at your chosen time and spot.",
                    "Read 5+ pages today. If the book bores you, you have permission to switch books guilt-free.",
                    "Read 10 minutes and tell someone (or text someone) one thing about what you read.",
                ],
            },
            {
                "title": "Momentum",
                "tasks": [
                    "Read 15-20 minutes today.",
                    "Read a full chapter (or 15 pages) today.",
                    "Read 15 minutes and write a 2-sentence summary of what happened or what you learned.",
                ],
            },
            {
                "title": "Reader habits",
                "tasks": [
                    "Read 25-30 minutes today, one stretch or split in two.",
                    "Start your 'to read next' list — add 3 books you're excited about.",
                    "Replace one scrolling session entirely with reading today.",
                ],
            },
            {
                "title": "Deep reading",
                "tasks": [
                    "Read 30+ minutes today and note one idea you disagree with or want to remember.",
                    "Finish the current book this week — read whatever it takes today to stay on pace.",
                    "Read somewhere new today (park, café, library) for 30 minutes.",
                ],
            },
            {
                "title": "Reading life",
                "tasks": [
                    "Read 40+ minutes today. Notice how much easier it is than week one.",
                    "Recommend a finished book to someone, with a real reason why.",
                    "Pick next month's books and set a page-per-day pace to finish them.",
                ],
            },
        ],
    },
    "fitness": {
        "name": "Get Stronger & Consistent",
        "emoji": "🏋️",
        "description": "Build workout consistency starting embarrassingly small, so you never skip.",
        "support_note": None,
        "levels": [
            {
                "title": "Showing up",
                "tasks": [
                    "Put on workout clothes and do exactly 1 minute of movement. That's the whole task.",
                    "Do 5 squats, 5 wall/knee pushups, and a 15-second plank. Done in 2 minutes.",
                    "Take a 10-minute walk. Set out your workout clothes for tomorrow before bed.",
                ],
            },
            {
                "title": "Micro workouts",
                "tasks": [
                    "Do 2 rounds: 10 squats, 5-10 pushups (any variation), 20-second plank.",
                    "Walk 15 minutes at a pace where talking is slightly harder.",
                    "Do 5 minutes of stretching or mobility, hitting hips, shoulders, and back.",
                ],
            },
            {
                "title": "Real sessions",
                "tasks": [
                    "Do a 10-minute workout: 3 rounds of squats, pushups, and plank. Rest as needed.",
                    "Do a 15-minute brisk walk/jog intervals: 1 minute faster, 1 minute easy.",
                    "Pick your 3 main exercises and write down today's reps — this is your baseline to beat.",
                ],
            },
            {
                "title": "Progressive overload",
                "tasks": [
                    "Beat one number from your last session: +1 rep, +5 seconds, or slightly harder variation.",
                    "Do a 20-minute full-body workout: squats, pushups, rows or lunges, plank. 3 rounds.",
                    "Add weight or difficulty to one exercise today (backpack with books counts).",
                ],
            },
            {
                "title": "Structured training",
                "tasks": [
                    "Do a 25-30 minute workout following a plan: 4-5 exercises, 3 sets each, logged.",
                    "Train one focus today (upper, lower, or core) for 25 minutes, then 5 minutes stretching.",
                    "Do 30 minutes of cardio you don't hate: bike, jog, swim, dance, hard walk.",
                ],
            },
            {
                "title": "Athlete mindset",
                "tasks": [
                    "Do a 35-40 minute session and log everything. Compare to 2 weeks ago.",
                    "Test yourself: max pushups, max squats in 1 minute, longest plank. Record it.",
                    "Plan next week's schedule (which days, which workouts) and put it in your calendar.",
                ],
            },
            {
                "title": "Built different",
                "tasks": [
                    "Do a 45-minute full session: warmup, strength work, conditioning finisher, stretch.",
                    "Retest your benchmarks and celebrate the gains — then set the next targets.",
                    "Bring someone with you today or share your progress — consistency loves company.",
                ],
            },
        ],
    },
    "porn_addiction": {
        "name": "Quit Porn",
        "emoji": "🧠",
        "description": "Rewire the habit loop with daily steps that shrink the pull and grow your real life.",
        "support_note": (
            "You're not broken and you're not alone — this is a common struggle. If it's severely "
            "affecting your life, a therapist who works with compulsive behaviors can genuinely help."
        ),
        "levels": [
            {
                "title": "Seeing the pattern",
                "tasks": [
                    "Write down your typical trigger chain: what time, what mood, what device, what leads to what.",
                    "Write one honest sentence about what quitting would give you back (time, energy, confidence, connection).",
                    "Count roughly how many hours last week went to it. Just the number, no shame spiral.",
                ],
            },
            {
                "title": "Adding friction",
                "tasks": [
                    "Install a content blocker or enable restricted mode on your most-used device today.",
                    "Ban the highest-risk device from the highest-risk room (usually phone + bedroom/bathroom).",
                    "Charge your phone outside your bedroom tonight.",
                ],
            },
            {
                "title": "Urge surfing",
                "tasks": [
                    "When an urge hits today: name it out loud ('this is an urge'), set a 10-minute timer, and do anything physical until it rings.",
                    "Practice one 'urge surf': sit with the urge for 5 minutes, breathing slowly, watching it rise and fall without acting.",
                    "Prepare your go-to urge response for tonight: 20 pushups, cold shower, or walk around the block. Pick one now.",
                ],
            },
            {
                "title": "Replacing the slot",
                "tasks": [
                    "Identify your most common usage time slot and pre-book it with a specific activity today.",
                    "Get 30 minutes of real-world dopamine today: exercise, music, sunlight, or an actual conversation.",
                    "Bored tonight? Do the boredom for 10 minutes instead of reaching for a screen. Boredom tolerance is a superpower.",
                ],
            },
            {
                "title": "Accountability",
                "tasks": [
                    "Tell one trusted person, or join an anonymous online community (like a recovery forum), today.",
                    "Write your 'relapse autopsy' template: 3 questions you'll answer if you slip (trigger? feeling? what next time?).",
                    "Set a weekly check-in reminder with yourself or your accountability contact.",
                ],
            },
            {
                "title": "Streak building",
                "tasks": [
                    "Full clean day today. If a slip happens, do the autopsy questions instead of bingeing on shame.",
                    "Plan your evening in advance today — the fight is won by not entering the ring.",
                    "Notice and write down one real-life benefit you've felt since starting (energy, focus, mood).",
                ],
            },
            {
                "title": "Free",
                "tasks": [
                    "Do something today that builds the life porn was numbing you from: socialize, create, train, apply.",
                    "Review your journey: triggers you've beaten, streak record, hardest moment survived. Write it down.",
                    "Write advice to someone starting day 1. You're now the person who knows the way.",
                ],
            },
        ],
    },
    "songwriting": {
        "name": "Better Songwriter",
        "emoji": "🎸",
        "description": "Write a little every day — finished songs come from tiny consistent reps.",
        "support_note": None,
        "levels": [
            {
                "title": "Collecting sparks",
                "tasks": [
                    "Write down 5 song title ideas. Bad ones count double — just fill the page.",
                    "Capture one real moment from today in 2-3 lines, like a lyric snapshot.",
                    "Voice-memo yourself humming any melody for 30 seconds. No judging allowed.",
                ],
            },
            {
                "title": "Daily fragments",
                "tasks": [
                    "Write 4 lines that rhyme (ABAB or AABB) about anything at all.",
                    "Steal a chord progression from a song you love and hum a NEW melody over it.",
                    "Rewrite one line from a favorite song in your own words. Notice what made the original work.",
                ],
            },
            {
                "title": "Building sections",
                "tasks": [
                    "Write one full verse (4-8 lines) on a single emotion. Don't edit while writing.",
                    "Write a chorus: one big simple idea, repeated hook line. Sing it 3 times.",
                    "Take yesterday's fragment (or any old one) and add a section to it.",
                ],
            },
            {
                "title": "Craft tools",
                "tasks": [
                    "Write a verse using one concrete image per line (things you can see/touch — no abstract words).",
                    "Write the same chorus idea 3 different ways, then pick the strongest.",
                    "Study one song you love: map its structure (verse/chorus/bridge), note where it lifts and why.",
                ],
            },
            {
                "title": "Full drafts",
                "tasks": [
                    "Finish a rough full song today: 2 verses + chorus. Ugly is fine, finished is the goal.",
                    "Write a bridge for any song draft — change the angle, chord, or perspective.",
                    "Co-write with a prompt: pick a random word and build a whole song section around it in 20 minutes.",
                ],
            },
            {
                "title": "Rewriting (the real writing)",
                "tasks": [
                    "Take a finished draft and rewrite the weakest line in every section.",
                    "Cut 20% of the words from one song. Say the same thing with less.",
                    "Record a rough voice memo demo of one song, start to finish.",
                ],
            },
            {
                "title": "Songwriter for real",
                "tasks": [
                    "Play or send one song to one person and ask for their honest first reaction.",
                    "Start your catalog: list your finished songs and pick the best one to polish this week.",
                    "Write today under constraint like a pro: 60 minutes, one sitting, one complete song.",
                ],
            },
        ],
    },
    "singing": {
        "name": "Better Singer",
        "emoji": "🎤",
        "description": "Daily voice training from gentle humming to confident full-voice performance.",
        "support_note": None,
        "levels": [
            {
                "title": "Waking the voice",
                "tasks": [
                    "Hum gently for 2 minutes — any notes, lips closed, feel the buzz in your face.",
                    "Do 2 minutes of lip trills (motorboat lips) sliding low to high. Silly = correct.",
                    "Breathe from your belly for 2 minutes: hand on stomach, it should push out on the inhale.",
                ],
            },
            {
                "title": "Gentle daily practice",
                "tasks": [
                    "Do 5 minutes: 2 min humming warmup, then hum along to one easy song you love.",
                    "Sing one song quietly in the shower or car, focusing on hitting the melody, not volume.",
                    "Do sirens for 3 minutes: slide 'oooo' from your lowest comfy note to highest and back.",
                ],
            },
            {
                "title": "Finding pitch",
                "tasks": [
                    "Match pitch: play 5 random notes (piano app works) and sing each back. Repeat any misses.",
                    "Record yourself singing one verse on your phone. Listen once. Note ONE thing to improve — only one.",
                    "Sing a simple scale (do-re-mi up and down) 5 times slowly on 'ah'.",
                ],
            },
            {
                "title": "Building technique",
                "tasks": [
                    "10-minute session: warmup, scales, then one song focusing ONLY on breathing at the right spots.",
                    "Sing one song and hold the last note of each phrase steady for its full length — no wobble goals.",
                    "Work your problem area for 10 minutes: the note or phrase you always miss, slowly, 10 times.",
                ],
            },
            {
                "title": "Voice with intent",
                "tasks": [
                    "Sing one song twice: once soft and gentle, once full and loud. Feel the difference in support.",
                    "Record this week's version of your practice song and compare to your first recording. Write what improved.",
                    "Practice dynamics: pick one song and deliberately go quiet-loud-quiet where the emotion calls for it.",
                ],
            },
            {
                "title": "Performance ready",
                "tasks": [
                    "Sing one full song start to finish, standing, no stopping or restarting — performance rules.",
                    "Sing in front of a mirror, working on relaxed face, jaw, and shoulders.",
                    "Learn one song slightly outside your comfort zone (higher, faster, or different style) — first pass today.",
                ],
            },
            {
                "title": "Sharing the voice",
                "tasks": [
                    "Sing for one person, live or via a sent recording. Butterflies are part of the rep.",
                    "Record your best take of your best song. Save it as your milestone.",
                    "Sing somewhere semi-public: campfire, karaoke, open mic, church, a jam — anywhere with ears.",
                ],
            },
        ],
    },
    "custom": {
        "name": "Custom Goal",
        "emoji": "✨",
        "description": "Your own goal, built on the universal ladder of habit-building.",
        "support_note": None,
        "levels": [
            {
                "title": "Define it",
                "tasks": [
                    "Write down exactly what 'better' looks like for this goal — one concrete sentence.",
                    "List the 3 smallest possible actions that move you toward this goal. Smaller than feels useful.",
                    "Decide when and where you'll work on this daily. Attach it to an existing habit (after coffee, before bed).",
                ],
            },
            {
                "title": "2-minute version",
                "tasks": [
                    "Do the 2-minute version of your goal activity today. Literally set a timer for 2 minutes.",
                    "Prepare your environment so tomorrow's 2 minutes is frictionless (lay out tools, open the app, clear the space).",
                    "Do 2 minutes, then write one sentence about how it felt to start.",
                ],
            },
            {
                "title": "Small daily reps",
                "tasks": [
                    "Do 5-10 minutes of focused work on your goal today.",
                    "Do your daily rep, then note one small thing that went better than last time.",
                    "Do your daily rep at your planned time and place, no negotiating with yourself.",
                ],
            },
            {
                "title": "Consistency engine",
                "tasks": [
                    "Do 15 minutes today. If motivation is low, commit to just 5 — you can stop after (you usually won't).",
                    "Track your streak visibly: mark today on a calendar or note where you'll see it.",
                    "Identify your #1 excuse for skipping and design a specific counter-move for it today.",
                ],
            },
            {
                "title": "Leveling up",
                "tasks": [
                    "Do 20+ minutes today and make it slightly harder than last week (more weight, harder piece, tougher problem).",
                    "Study someone great at this for 10 minutes, then practice one thing you noticed.",
                    "Do your rep, then ask: what's the 20% of this practice giving 80% of my progress? Do more of that.",
                ],
            },
            {
                "title": "Testing yourself",
                "tasks": [
                    "Measure your progress today against week one, concretely. Write down the before/after.",
                    "Do your practice in a higher-stakes way today: timed, observed, recorded, or published.",
                    "Get feedback from one person who knows this area better than you.",
                ],
            },
            {
                "title": "Mastery mindset",
                "tasks": [
                    "Do a full deep session (30-45 min) with zero distractions — phone in another room.",
                    "Help or teach someone else one thing about this. Teaching cements skill.",
                    "Set your next milestone beyond this program and write the first step toward it.",
                ],
            },
        ],
    },
}


def get_goal_options():
    """Return (key, label) pairs for the goal picker, custom last."""
    items = [(k, f"{v['emoji']} {v['name']}") for k, v in GOAL_LIBRARY.items() if k != "custom"]
    items.append(("custom", f"{GOAL_LIBRARY['custom']['emoji']} Something else (custom goal)"))
    return items
