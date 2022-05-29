"""Typing test implementation"""

from utils import lower, split, remove_punctuation, lines_from_file
from ucb import main, interact, trace
from datetime import datetime


###########
# Phase 1 #
###########


def choose(paragraphs, select, k):
    """Return the Kth paragraph from PARAGRAPHS for which SELECT called on the
    paragraph returns true. If there are fewer than K such paragraphs, return
    the empty string.
    """
    # BEGIN PROBLEM 1
    "*** YOUR CODE HERE ***"
    # END PROBLEM 1
    candidate = [p for p in paragraphs if select(p)]
    if k >= len(candidate):
        return ""
    else:
        return candidate[k]



def about(topic):
    """Return a select function that returns whether a paragraph contains one
    of the words in TOPIC.

    >>> about_dogs = about(['dog', 'dogs', 'pup', 'puppy'])
    >>> choose(['Cute Dog!', 'That is a cat.', 'Nice pup!'], about_dogs, 0)
    'Cute Dog!'
    >>> choose(['Cute Dog!', 'That is a cat.', 'Nice pup.'], about_dogs, 1)
    'Nice pup.'
    """
    assert all([lower(x) == x for x in topic]), 'topics should be lowercase.'
    # BEGIN PROBLEM 2
    "*** YOUR CODE HERE ***"
    # END PROBLEM 2
    def select(paragraph):

        paragraph = split(remove_punctuation(lower(paragraph)))
        for word in topic:
            if word in paragraph:
                return True
        return False

    return select


def accuracy(typed, reference):
    """Return the accuracy (percentage of words typed correctly) of TYPED
    when compared to the prefix of REFERENCE that was typed.

    >>> accuracy('Cute Dog!', 'Cute Dog.')
    50.0
    >>> accuracy('A Cute Dog!', 'Cute Dog.')
    0.0
    >>> accuracy('cute Dog.', 'Cute Dog.')
    50.0
    >>> accuracy('Cute Dog. I say!', 'Cute Dog.')
    50.0
    >>> accuracy('Cute', 'Cute Dog.')
    100.0
    >>> accuracy('', 'Cute Dog.')
    0.0
    """
    typed_words = split(typed)
    reference_words = split(reference)
    # BEGIN PROBLEM 3
    "*** YOUR CODE HERE ***"
    # END PROBLEM 3
    type_words = split(typed)
    refer_words = split(reference)
    match, total = 0, len(type_words)
    for i in range(min(total, len(refer_words))):
        if type_words[i] == refer_words[i]:
            match += 1
    return match / total * 100.0 if total != 0 else 0.0




def wpm(typed, elapsed):
    """Return the words-per-minute (WPM) of the TYPED string."""
    assert elapsed > 0, 'Elapsed time must be positive'
    # BEGIN PROBLEM 4
    "*** YOUR CODE HERE ***"
    # END PROBLEM 4
    char_sum = len(typed)
    return (char_sum / 5) / (elapsed / 60)



def autocorrect(user_word, valid_words, diff_function, limit):
    """Returns the element of VALID_WORDS that has the smallest difference
    from USER_WORD. Instead returns USER_WORD if that difference is greater
    than LIMIT.
    """
    # BEGIN PROBLEM 5
    "*** YOUR CODE HERE ***"
    # END PROBLEM 5
    if user_word in valid_words:
        return user_word
    else:
        ret_word = user_word
        min_diff = 10000
        for word in valid_words:
            diff = diff_function(user_word, word, limit)
            if min_diff > diff and diff <= limit:
                min_diff = diff
                ret_word = word
        return ret_word




def shifty_shifts(start, goal, limit):
    """A diff function for autocorrect that determines how many letters
    in START need to be substituted to create GOAL, then adds the difference in
    their lengths.
    """
    # BEGIN PROBLEM 6
    # END PROBLEM 6
    if start == "" or goal == "":
        return max(len(start), len(goal))

    if limit == -1:
        # this means all limit has been consumed
        return 1
    else:
        if start[0] != goal[0]:
            # this situation means we consume one of limit
            all_but_first = shifty_shifts(start[1:], goal[1:], limit - 1)
            return 1 + all_but_first
        else:
            # this situation means we needn't consume limit
            all_but_first = shifty_shifts(start[1:], goal[1:], limit)
            return all_but_first


def pawssible_patches_v0(start, goal, limit):
    assert False, "remove this line"
    if ____________: # Fill in the condition
        # BEGIN
        "*** YOUR CODE HERE ***"
        # END
    elif ___________: # Feel free to remove or add additional cases
        # BEGIN
        "*** YOUR CODE HERE ***"
        # END

    else:
        add_diff = ... # Fill in these lines
        remove_diff = ...
        substitute_diff = ...
        # BEGIN
        "*** YOUR CODE HERE ***"
        # END
def pawssible_patches(start, goal, limit):
    """A diff function that comptes the edit distance from START to GOAL."""
    def diff(start, goal):
        """if I want to remove or add some elements of/to start,
        I will change xxxx elements.
        return xxxx
        """
        if start.find(goal[0]) != -1:
            return start.find(goal[0])
        else:
            return len(start)
    # recurision base: there exists empty string or all limit has been consumed
    if start == "" or goal == "":
        return max(len(start), len(goal))
    if limit == -1:
        return 1
    else:
        if start[0] != goal[0]:
            # this situation we may choose one of three types of operation,
            # which need the least times of operation
            local_add_diff = diff(goal, start)
            local_remove_diff = diff(start, goal)

            add_diff = local_add_diff + pawssible_patches(goal[:local_add_diff] + start, goal, limit - local_add_diff)
            remove_diff = local_remove_diff + pawssible_patches(start[local_remove_diff:], goal, limit - local_remove_diff)
            substitute_diff = 1 + pawssible_patches(start[1:], goal[1:], limit - 1)
            min_diff = min(add_diff, remove_diff, substitute_diff)
            if min_diff > limit:
                return limit + 1
            else:
                return min_diff
        else:
            return pawssible_patches(start[1:], goal[1:], limit)




def final_diff(start, goal, limit):
    """A diff function. If you implement this function, it will be used."""
    assert False, 'Remove this line to use your final_diff function'


###########
# Phase 3 #
###########


def report_progress(typed, prompt, user_id, send):
    """Send a report of your id and progress so far to the multiplayer server."""
    # BEGIN PROBLEM 8
    "*** YOUR CODE HERE ***"
    # END PROBLEM 8
    assert len(typed) <= len(prompt), "len typed shouldn't be larger than len prompt"
    i, total = 0, len(prompt)

    while i < len(typed):
        if typed[i] == prompt[i]:
            i += 1
        else:
            break
    progress = i/total * 1.0
    send({"id": user_id, "progress": progress})
    return progress

def fastest_words_report(times_per_player, words):
    """Return a text description of the fastest words typed by each player."""
    game = time_per_word(times_per_player, words)
    fastest = fastest_words(game)
    report = ''
    for i in range(len(fastest)):
        words = ','.join(fastest[i])
        report += 'Player {} typed these fastest: {}\n'.format(i + 1, words)
    return report


def time_per_word(times_per_player, words):
    """Given timing data, return a game data abstraction, which contains a list
    of words and the amount of time each player took to type each word.

    Arguments:
        times_per_player: A list of lists of timestamps including the time
                          the player started typing, followed by the time
                          the player finished typing each word.
        words: a list of words, in the order they are typed.
    """
    # BEGIN PROBLEM 9
    "*** YOUR CODE HERE ***"
    # END PROBLEM 9
    times = []
    # for each player, we compute the time consumed for each word,
    # remember the first time is the start time
    for i in range(len(times_per_player)):
        cur = []
        for j in range(len(times_per_player[i]) - 1):
            cur.append(times_per_player[i][j + 1] - times_per_player[i][j])
        times.append(cur)
    return game(words, times)


def fastest_words(game):
    """Return a list of lists of which words each player typed fastest.

    Arguments:
        game: a game data abstraction as returned by time_per_word.
    Returns:
        a list of lists containing which words each player typed fastest
    """
    player_indices = range(len(all_times(game)))  # contains an *index* for each player
    word_indices = range(len(all_words(game)))    # contains an *index* for each word
    # BEGIN PROBLEM 10
    "*** YOUR CODE HERE ***"
    # END PROBLEM 10
    def find_min(game, i):
        """find the min item index of ith col of times
        """
        min_idx = 0
        for j in player_indices:
            if time(game, j, i) < time(game, min_idx, i):
                min_idx = j
        return min_idx

    fatest_per_player = [[] for _ in player_indices]
    for i in word_indices:
        # for each i word, find the j player which typed fastest
        j = find_min(game, i)
        fatest_per_player[j].append(word_at(game, i))
    return fatest_per_player





def game(words, times):
    """A data abstraction containing all words typed and their times."""
    assert all([type(w) == str for w in words]), 'words should be a list of strings'
    assert all([type(t) == list for t in times]), 'times should be a list of lists'
    assert all([isinstance(i, (int, float)) for t in times for i in t]), 'times lists should contain numbers'
    assert all([len(t) == len(words) for t in times]), 'There should be one word per time.'
    return [words, times]


def word_at(game, word_index):
    """A selector function that gets the word with index word_index"""
    assert 0 <= word_index < len(game[0]), "word_index out of range of words"
    return game[0][word_index]


def all_words(game):
    """A selector function for all the words in the game"""
    return game[0]


def all_times(game):
    """A selector function for all typing times for all players"""
    return game[1]


def time(game, player_num, word_index):
    """A selector function for the time it took player_num to type the word at word_index"""
    assert word_index < len(game[0]), "word_index out of range of words"
    assert player_num < len(game[1]), "player_num out of range of players"
    return game[1][player_num][word_index]


def game_string(game):
    """A helper function that takes in a game object and returns a string representation of it"""
    return "game(%s, %s)" % (game[0], game[1])

enable_multiplayer = False  # Change to True when you're ready to race.

##########################
# Command Line Interface #
##########################


def run_typing_test(topics):
    """Measure typing speed and accuracy on the command line."""
    paragraphs = lines_from_file('data/sample_paragraphs.txt')
    select = lambda p: True
    if topics:
        select = about(topics)
    i = 0
    while True:
        reference = choose(paragraphs, select, i)
        if not reference:
            print('No more paragraphs about', topics, 'are available.')
            return
        print('Type the following paragraph and then press enter/return.')
        print('If you only type part of it, you will be scored only on that part.\n')
        print(reference)
        print()

        start = datetime.now()
        typed = input()
        if not typed:
            print('Goodbye.')
            return
        print()

        elapsed = (datetime.now() - start).total_seconds()
        print("Nice work!")
        print('Words per minute:', wpm(typed, elapsed))
        print('Accuracy:        ', accuracy(typed, reference))

        print('\nPress enter/return for the next paragraph or type q to quit.')
        if input().strip() == 'q':
            return
        i += 1


@main
def run(*args):
    """Read in the command-line argument and calls corresponding functions."""
    import argparse
    parser = argparse.ArgumentParser(description="Typing Test")
    parser.add_argument('topic', help="Topic word", nargs='*')
    parser.add_argument('-t', help="Run typing test", action='store_true')

    args = parser.parse_args()
    if args.t:
        run_typing_test(args.topic)