"""
Running motivational quotes for TRMNL dashboard.
"""

QUOTES = [
    "The miracle isn't that I finished. The miracle is that I had the courage to start.",
    "Run when you can, walk if you have to, crawl if you must; just never give up.",
    "It's not about how fast you run, or how far you run. It's about running the race you were meant to run.",
    "The only bad run is the one that didn't happen.",
    "Running is nothing more than a series of arguments between the part of your brain that wants to stop and the part that wants to keep going.",
    "Pain is temporary. Quitting lasts forever.",
    "Your legs are not giving out. Your head is giving up. Keep going.",
    "The will to win means nothing without the will to prepare.",
    "Every morning in Africa, a gazelle wakes up. It knows it must run faster than the fastest lion or it will be killed. Whether you are a lion or a gazelle, when the sun comes up, you better be running.",
    "If you run, you are a runner. It doesn't matter how fast or how far.",
    "Running is the greatest metaphor for life, because you get out of it what you put into it.",
    "Ask yourself: 'Can I give more?' The answer is usually yes.",
    "We run, not because we think it is doing us good, but because we enjoy it and cannot help ourselves.",
    "Run often. Run long. But never outrun your joy of running.",
    "The body achieves what the mind believes.",
    "I don't run to add days to my life, I run to add life to my days.",
    "Running teaches you that life is not a race, it's a journey to be savored.",
    "Believe in yourself and all that you are. Know that there is something inside you that is greater than any obstacle.",
    "The obsession with running is really an obsession with the potential for more and more life.",
    "Make running your daily habit. Not because you want to, but because you can.",
]


def get_daily_quote():
    """
    Get a random quote on each request.
    """
    import random
    
    return random.choice(QUOTES)
