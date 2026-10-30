with open(r"C:\Users\saira\Desktop\input.txt", "r") as file:
    words = file.read().lower().split()

word_counts = {}
for word in words:
    word_counts[word] = word_counts.get(word, 0) + 1

with open("output.txt", "w") as file:
    for word, count in word_counts.items():
        file.write(f"{word}: {count}\n")
        print(f"{word}: {count}")