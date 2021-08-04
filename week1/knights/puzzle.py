from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    # Structural constraints
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),
    # If A is truthful (Knight) then A is both Knight and Knave
    Implication(AKnight, And(AKnight, AKnave)),
    # If A is lying (Knave) then A is not both Knight and Knave
    Implication(AKnave, Not(And(AKnight, AKnave)))
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    # Structural constraints
    Or(AKnight, AKnave),
    Or(BKnight, BKnave),
    Not(And(AKnight, AKnave)),
    Not(And(BKnight, BKnave)),
    # If A is truthful (Knight) then both are Knaves
    Implication(AKnight, And(AKnave, BKnave)),
    # If A is lying (Knave) then either can be Knaves but not both
    Implication(AKnave, Not(And(AKnave, BKnave)))
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    # Structural constraints
    Or(AKnight, AKnave),
    Or(BKnight, BKnave),
    Not(And(AKnight, AKnave)),
    Not(And(BKnight, BKnave)),
    # If A is truthful (Knight) then they are both Knights or both Knaves
    Implication(AKnight, Biconditional(AKnight, BKnight)),
    # If A is lying (Knave) then they are not both Knights or both Knaves
    Implication(AKnave, Not(Biconditional(AKnight, BKnight))),
    # If B is truthful (Knight) then they cannot be both Knights or both Knaves
    Implication(BKnight, Not(Biconditional(AKnight, BKnight)))
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    # Structural constraints
    Or(AKnight, AKnave),
    Or(BKnight, BKnave),
    Or(CKnight, CKnave),
    Not(And(AKnight, AKnave)),
    Not(And(BKnight, BKnave)),
    Not(And(CKnight, CKnave)),
    # If B is truthful (Knight) and A is truthful (Knight) then A is a Knave
    Implication(And(BKnight, AKnight), AKnave),
    # If B is truthful (Knight) and A is lying (Knave) then A is a Knight
    Implication(And(BKnight, AKnave), AKnight),
    # If B is truthful (Knight) then C is a Knave, if lying then C is a Knight
    Biconditional(BKnight, CKnave),
    # If C is truthful (Knight) then A is a Knight, if lying then A is a Knave
    Biconditional(CKnight, AKnight)
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
