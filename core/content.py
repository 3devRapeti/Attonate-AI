"""
Real marketing copy for the Attonate site, carried over verbatim from the
original React component (TaxonLanding.jsx — the codebase's original
working name before the Attonate rebrand). No fabricated stats or
testimonials — per an earlier explicit decision, this is an early-stage
company and the copy reflects genuine commitments/policies instead of a
track record we don't have yet.

Icon values are lucide icon names (kebab-case) rendered client-side via
the lucide CDN script — see templates/base.html.
"""

CONTENT = {
    "client": {
        "nav_links": ["Solutions", "Pricing", "Blog", "Company"],
        "hero": {
            "title": ["Enterprise Data Labeling", "for Modern AI."],
            "subtitle": (
                "Transform raw data into high-quality training sets for complex "
                "machine learning models. Built for enterprise AI teams."
            ),
            "cta": "Explore Platform",
        },
        "commitments": {
            "heading": "Why work with a new platform",
            "subtext": "We're an early-stage team — here's what we commit to instead of a track record.",
            "items": [
                {
                    "icon": "handshake",
                    "title": "Pilot Before You Commit",
                    "desc": "Start with a small paid pilot batch before any long-term agreement — see the quality firsthand.",
                },
                {
                    "icon": "users",
                    "title": "Direct Access to the Team",
                    "desc": "You work directly with the people building the platform, not a support queue.",
                },
                {
                    "icon": "file-check",
                    "title": "NDA on Every Project",
                    "desc": "Every annotator signs a confidentiality agreement before touching your data, even on trial work.",
                },
                {
                    "icon": "banknote",
                    "title": "Usage-Based Pricing",
                    "desc": "Pay only for what you label — no platform fees, no long-term lock-in.",
                },
            ],
        },
        "features": [
            {
                "icon": "check",
                "title": "Labeling",
                "desc": "Simple outline annotation with the 2px strokes and rounded edges.",
                "cta": "Get a Demo",
                "filled": True,
            },
            {
                "icon": "move",
                "title": "Annotation Types",
                "desc": "Image, text, audio, video and multimodal annotation in one workspace.",
                "cta": "Annotation Types",
                "filled": False,
            },
            {
                "icon": "check-circle-2",
                "title": "Quality Assurance",
                "desc": "Consensus scoring and dedicated QA leads on every enterprise project.",
                "cta": "View Metrics",
                "filled": False,
            },
            {
                "icon": "layers",
                "title": "Premium Annotation",
                "desc": "Advanced, high-quality labeling services and tools.",
                "cta": "Explore Tiers",
                "filled": True,
            },
        ],
        "steps": [
            {
                "title": "Define your taxonomy",
                "desc": "Set annotation guidelines, label schemas, and quality thresholds tailored to your model.",
            },
            {
                "title": "Get matched with experts",
                "desc": "We route your project to vetted specialists with the right domain expertise.",
            },
            {
                "title": "Review at scale",
                "desc": "Track throughput and accuracy in real time with built-in QA and consensus scoring.",
            },
            {
                "title": "Export & integrate",
                "desc": "Pull labeled data directly into your pipeline via API, SDK, or bulk export.",
            },
        ],
        "dashboard": {
            "heading": "See the platform your team gets access to",
            "subtext": "Manage taxonomies, review annotations, and monitor quality — all from one workspace.",
        },
        "extra": {
            "type": "security",
            "heading": "Built for enterprise trust",
            "subtext": "Security and compliance baked into every project.",
            "items": [
                {
                    "icon": "lock",
                    "title": "SOC 2 Type II",
                    "desc": "Independently audited controls for data security and availability.",
                },
                {
                    "icon": "shield-check",
                    "title": "Data Privacy by Design",
                    "desc": "Encryption at rest and in transit, with configurable retention policies.",
                },
                {
                    "icon": "file-check",
                    "title": "NDA-backed Workforce",
                    "desc": "Every annotator signs enforceable confidentiality agreements before access.",
                },
                {
                    "icon": "building-2",
                    "title": "Dedicated Infrastructure",
                    "desc": "Isolated environments available for regulated or sensitive workloads.",
                },
            ],
        },
        "faq": [
            {
                "q": "What types of data can Attonate label?",
                "a": "Image, text, audio, video, and multimodal data — including bounding boxes, segmentation, transcription, and RLHF preference ranking.",
            },
            {
                "q": "How fast can a project start?",
                "a": "Most projects begin within 48 hours of taxonomy approval, with pilot batches often ready the same week.",
            },
            {
                "q": "What quality guarantees do you offer?",
                "a": "We back every project with a quality SLA, consensus-based review, and dedicated QA leads for enterprise accounts.",
            },
            {
                "q": "Can we bring our own annotation tool?",
                "a": "Yes. Attonate integrates via API, or your team can use our native annotation workspace out of the box.",
            },
        ],
        "cta": {
            "title": ["Ready to scale your", "AI development?"],
            "primary": "Get a Demo",
            "secondary": "Read Documentation",
        },
    },
    "user": {
        "nav_links": ["How it Works", "Earnings", "Community", "Resources"],
        "hero": {
            "title": ["You're Training The AI", "That Changes Everything."],
            "subtitle": (
                "Every task you complete teaches AI to see, read, and judge a little "
                "better. You're one of the first people on earth doing this work — "
                "and you're paid well for it, every step of the way."
            ),
            "cta": "Apply as an Expert",
        },
        "impact": {
            "heading": "You're not just completing tasks.",
            "subtext": (
                "Every label, every review, every judgment call becomes part of how "
                "AI learns to understand the world. The models being trained today "
                "will shape how entire industries work tomorrow — and you're one of "
                "the people building that foundation, right now, before almost "
                "anyone else."
            ),
        },
        "commitments": {
            "heading": "What we promise from day one",
            "subtext": "We're a brand-new platform — these are commitments, not stats we're claiming.",
            "items": [
                {
                    "icon": "banknote",
                    "title": "Every Task Is Paid",
                    "desc": "No unpaid trial tasks or onboarding busywork — you're paid from your very first task.",
                },
                {
                    "icon": "calendar-check",
                    "title": "Weekly Payouts, On Time",
                    "desc": "Get paid every week for completed work, with no delays.",
                },
                {
                    "icon": "message-square",
                    "title": "Direct Feedback Loop",
                    "desc": "Talk directly with the team building the platform — your feedback shapes how tasks are designed.",
                },
                {
                    "icon": "clock",
                    "title": "Work On Your Terms",
                    "desc": "No fixed hours or quotas. Pick up tasks whenever it fits your schedule.",
                },
            ],
        },
        "features": [
            {
                "icon": "clock",
                "title": "Flexible Hours",
                "desc": "Work whenever it suits you — no minimum hours, no fixed shifts.",
                "cta": "See Open Tasks",
                "filled": True,
            },
            {
                "icon": "wallet",
                "title": "Transparent Pay",
                "desc": "Know your rate before you start. Get paid weekly, with no hidden deductions.",
                "cta": "View Pay Rates",
                "filled": False,
            },
            {
                "icon": "user-check",
                "title": "Skill-Matched Work",
                "desc": "Tasks matched to your background, from general labeling to specialist review.",
                "cta": "Take Skills Test",
                "filled": False,
            },
            {
                "icon": "trending-up",
                "title": "Grow Your Rate",
                "desc": "As your judgment sharpens, so does your impact — build a track record and unlock higher-paying, specialized work over time.",
                "cta": "Learn More",
                "filled": True,
            },
        ],
        "steps": [
            {"title": "Apply in minutes", "desc": "Tell us about your background and areas of expertise."},
            {"title": "Get vetted", "desc": "Complete a short skills assessment matched to your domain."},
            {"title": "Start working", "desc": "Pick up available tasks that fit your schedule and expertise."},
            {"title": "Get paid weekly", "desc": "Track your earnings in real time and cash out every week."},
        ],
        "dashboard": {
            "heading": "This is where you'll do the work",
            "subtext": "A guided workspace with clear instructions, examples, and instant feedback on every task.",
        },
        "extra": {
            "type": "earnings",
            "heading": "Transparent, tiered pay",
            "subtext": "Rates scale with the skill and judgment each task requires.",
            "tiers": [
                {
                    "title": "General Labeling",
                    "rate": "$12–18/hr",
                    "desc": "Image tagging, transcription, basic classification.",
                },
                {
                    "title": "Specialist Review",
                    "rate": "$25–45/hr",
                    "desc": "Domain-specific annotation, RLHF ranking, quality review.",
                },
                {
                    "title": "Expert Evaluation",
                    "rate": "$50–120/hr",
                    "desc": "Professional judgment tasks for medical, legal, and technical domains.",
                },
            ],
            "note": "Paid weekly via direct deposit or PayPal. No minimum payout threshold.",
        },
        "faq": [
            {
                "q": "Do I need experience to start?",
                "a": "No prior annotation experience is required for general tasks. Specialist and expert tiers may require relevant credentials.",
            },
            {
                "q": "How and when do I get paid?",
                "a": "Payments are issued weekly via direct deposit or PayPal, with no minimum payout threshold.",
            },
            {
                "q": "How many hours do I need to work?",
                "a": "There's no minimum. Pick up tasks whenever you're available — it's entirely self-paced.",
            },
            {
                "q": "What equipment do I need?",
                "a": "A reliable computer and internet connection. Some specialist tasks may require a webcam for verification.",
            },
        ],
        "cta": {
            "title": ["Ready to help build", "what comes next?"],
            "primary": "Apply Now",
            "secondary": "See Open Roles",
        },
    },
}
