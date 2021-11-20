# Fushigi no Yume no Alice Translation Process
(description by 4lorn5)

![Test Image 1](https://i.ibb.co/1LXynV1/TITLE2.png)

After our past work on Wonder Momo, me and Dave Shadoff started looking into more PC Engine games which have remained untranslated for decades. It's actually an easy task; fan translation groups will often flock toward more popular platforms, with consoles such as the Super Nintendo gaining the bulk of the attention. This is by no means a criticism; the amount of documentation and proliferation of fanmade utilities that benefit translation efforts are often more geared towards NEC's 16-bit contemporaries. But the end result is still that of a much higher ratio of SNES or Genesis translations per year, while the PC Engine languishes in somewhat relative obscurity.

As I write this, we are currently and actively involved in several PC Engine translations. One of these, an English translation patch for Fushigi no Yume no Alice, was recently released, and we've decided to explore some of the changes made in the game. I should note that we wouldn't have progressed as quickly without the assistance of MooZ (https://github.com/BlockoS), who was instrumental in locating some of the more vital routines in the game.

So, our workflow required the following:

•Find the Japanese text in the ROM

•Understand text control codes, if any

•Insert a new font and reinsert the script

•Localize and change the title screen logo

•Localize some of the graphics

•Timing issues

•Find a good way to playtest changes


## Find the Japanese text in the ROM

The process was virtually identical to the one used for Wonder Momo: load up the ROM in Mednafen and make use of its visual debugger features. For a more extensive explanation on the basics of finding character codes for dialogue strings with Mednafen, [please visit our Wonder Momo repository](https://github.com/4lorn5/MomoTG16/tree/main/translation%20process).

We soon found that filler, who had translated Wonder Momo, had previously extracted the script from, and generated a table file for the Alice ROM. This served as a basis for our translation, as it allowed us to quickly cover some ground: the introductory text, the character dialogues, and the ending text. During playtesting, however, we soon realized that not all text had been extracted. It was necessary to find the text for the Magic Books, one of Alice's weapons against the warped Wonderland creatures she encounters; as well as the text of the ending credits, listing not only developer names but also all of the game's characters and enemies.

There is also a hidden Sound Test mode, where it's casually mentioned there is (or rather, there was) a CD Soundtrack released for Fushigi no Yume no Alice, but this mode is only accessible through a secret code input at the title screen (more on this later).


## Understand text control codes, if any

As expounded on in the Wonder Momo repository, code will vary from game to game. Even a game that makes no use of diacritics will still need some manner of control over spacing, line breaks, or closing and/or opening text boxes. Alice is no different, of course; it just has the added peculiarity of using colored text and character pictures with a rudimentary animation function in its intro and ending texts.

To begin with, we load the ROM and wait until the title screen finishes animating the logo and the music stops - a second later and it fades to black, leading players to the intro.

![Test Image 2](https://i.ibb.co/w43T7bP/Alice-1.png)

As shown above, regular text is in white but certain words are curious. Namely, "Alice" (アリス), "rabbit" (ウサギ), "fairy tales" (ドウワ), "dreams" (ゆめ) and "demons" or "apparations" (マモノ) will make use of a specific color when printed on screen ("rabbit" and "fairy tales" share the same one). Thankfully, there was no specific routine involved: the game simply includes colored characters on its font set.

![Test Image 3](https://i.ibb.co/Xj8086X/Alice-2.png)

Portraits are curioser: they're still frames that will slide from left to right depending on which character takes center stage in the ongoing narration. It begins with Alice dreaming), whose dream is then invaded by demons, which frightens Alice, but then a Rabbit appears, and then it cuts back to Alice as she decides to save everyone and end the nightmare by confronting the demons.

With filler's extracted script, it was easy to see where these were - they're strewn across the intro text itself.

![Test Image 4](https://i.ibb.co/0f3BmXd/Alice-3.png)

Note the character codes among the text, with values such as 0x06 and 0x04 appearing in the middle of the words. Even for the untrained eye, it's easy to see how these are extra code. For one, the value is too low compared to the rest of the alphabet (one of the control values is 0x04, which stands in stark contrast with the first Japanese character in the font's tilemap, あ, with a value of 34). Also, while most games' encoding would print out an actual "4" or "6" with this kind of value, no numeral is shown at all. But if any doubt remains as to whether these ocasional values are character control codes, one needs only to keep looking at the script and the intro, until they reach this point:

![Test Image 5](https://i.ibb.co/grJ9TB3/Alice-4.png)

Notice how the Rabbit's mouth is moving to give off the impression he's talking? Now, let's look at the relevant part of the intro where this happens:

![Test Image 6](https://i.ibb.co/2KhdNgR/Alice-5.png)

Notice the pattern? For the intro and ending (more on that later), the game uses a specific set of control codes not only for switching portraits, but also to simulate animated sprites. 0x0F and 0x10 are used as "state" indicators, with one value calling into display the Rabbit's mouth closed, and the other calling into display his mouth open (truth be told, it's merely toggling the visibility of the open mouth sprites over his standard, static portrait). Knowing this, any user can adjust the timing of the animations to suit their translation needs - or even remake it, should they desire to.

The primary text controls are associated with values 0x01 (single space), 0x02 (line break), and 0x03 (end text box).

The next step involved fishing for the remaining text. We had the intro and ending, but were still missing out on the ending credits and Magic Books. Because Magic Books are accessible during gameplay, with a new one added to Alice's repertoire at the end of each main level, it was easier to search for, and find these names during playtesting. Starting with Stage 1, we pause the game then press Button I, which opens this menu:

![Test Image 7](https://i.ibb.co/Jr05NNh/Alice-9.png)

Literally, the first Magic Book at Alice's disposal is called "Red Magic", which allows her a temporary glimpse into hidden power-ups in her surroundings. Notice one important detail when compared to the intro text, however: diacritics are not written right after letters, but above them. With this is mind, we do a value search for the corresponding letters: レット マシック, which, according to filler's provided table, translates to A9 AE 93 01 9E 8B AE 87 01. Searching the ROM, we find such a value:

![Test Image 7](https://i.ibb.co/7zNBVpL/Alice-6.png) 

![Test Image 8](https://i.ibb.co/GTLzy7B/Alice-7.png) 

According to our table, the diacritic ” equals a character value of 66. So why is it not present in this specific line of code? Because it's printing them a line above. Let's look more carefully at the "Red Magic" string:

![Test Image 8](https://i.ibb.co/tbSdLKt/Alice-8.png)

As expected, they're found throughout this portion of code, with 0x01 representing an empty space and 0x66 the ” diacritic, both set a line above; and the next line printing the "Red Magic" name. Every spell in Alice is defined as a Magic Book, and is color-coded: Red Magic, Blue Magic, and so on. For our translation, we opted to replace the diacritics line with the first name, or color, of the book, and use the second line to simply print "Magic".

![Test Image 9](https://i.ibb.co/Lr1BZ9H/Alice-10.png)

For reference, the names of Magic Books themselves (without diacritics) are located at:

```
レッド マジック
Red Magic
A9 AE 93 01 9E 8B AE 87 01
Between offsets 595F and 5967
```
```
ブルー マジック
Blue Magic
9B A8 6F 01 9E 8B AE 87 01
Between offsets 5971 and 5979
```
```
グリーン マジック
Green Magic
87 2A 6F AD 01 9E 8B AE 87
Between offsets 5983 and 598B
```
```
シルバー マジック
Silver Magic
8B A8 99 6F 01 9E 8B AE 87
Between offsets 5995 and 599D
```
```
ゴールド マジック
Gold Magic
89 6F A8 93 01 9E 8B AE 87
Between offsets 59A7 and 59AF
```

Next were the dialogues. While filler's extracted script pointed us in the right direction, and we quickly found them between offsets 4BACD and 4BC8E, these provided a challenge.

![Test Image 10](https://i.ibb.co/k42y4d7/Alice-dialogues.png)

To explain them, it's necessary to explain how the game works regarding these. In Alice, several characters were kidnapped, while others underwent... some changes. Before the final stages kick in, most stages are comprised of 3 sub-stages, such as Forest 1, Forest 2, and Forest 3. As each guardian of a sub-stage is defeated, rescued characters will thank Alice, give hints or, as is the case with defeating a stage's boss, receive a Magic Book. All characters will first greet Alice, then display different messages.

![Test Image 11](https://i.ibb.co/TRLsg4g/Alice-15.png)

But while every character on a given sub-stage will have specific lines, their greetings are always the same. So, once rescued, the Rabbit in sub-stage 1, the Rabbit in sub-stage 2, and Cinderella in sub-stage 3 will always say the same "Thank you". This wouldn't be an issue, except the line itself is only stored once, and the game simply references again when needed. In terms of code and text, what this means is that the game stores all dialogue lines one after another in order of appearance, but will only store these greetings once, for the very first time they are used. Further, in order to save additional space, the developers decided to have two characters whose last line when presenting Alice with a book are also the same - so it was necessary to produce a translation that took this into account.

![Test Image 12](https://i.ibb.co/rvsSktq/Alice-14.png)
*The two characters in question.*

There were two other outstanding issues, however, one being character limit. It would be necessary to considerably rework the dialogue box system to make it accept more characters per line, so in the end it was decided to cut down on my translation to fit within the 14 character per line constrain. Another issue, somewhat easier to solve, was that the dialogue system also uses diacritics - but not in the same way as the Magic Books, at least when it comes to code.

One of the most basic pieces of advice given to romhacking newbies for the purposes of translations is that, once a text block is found, one needs to look nearby for its table. It's sage advice and, in normal circumstances, it works - it might simply be several offsets before or after it, provided the developers also played it safe. Alice is one of those normal circumstances, for instance. Right before the dialogues located between offsets 4BACD and 4BC8E, the table for the dialogue is also found right between 4BA87 and 4BACC:

![Test Image 13](https://i.ibb.co/m6Wm3th/Alice-dialogue-table.png)

These are actually fairly intuitive. The first dialogue line, the greeting shared by the rabbits and Cinderella, is set between 4BACD and 4BAD9. Meanwhile, the first dialogue pointer is found at offset 4BA87, and indicates the value CD 7A. Remembering that the PC Engine's HuC6280 architecture is little-endian, meaning it stores the least-significant byte at the smallest address, makes it easier to understand. Another way of thinking of how it handles data is that it reverses byte importance. Example:

```
		Pointer		Pointer value reversed		Offset where text begins	
1st dialogue	  CD 7A		     7A CD = XXACD			4BA CD	
2nd dialogue	  DA 7A		     7A DA = XXADA			4BA DA
```

And so on. 7A will represent the starting offset, in this case, 4BAXX. 7B is referencing an offset starting with 4BBXX, and 7C is addressing an offset starting with 4BCXX. The only additional info necessary to keep in mind was that character value 0xFF was used to declare the end of a sentence.

But what about those diacritics?

![Test Image 14](https://i.ibb.co/hWhC8nL/Alice-16.png)

The way the game uses diacritics in dialogues threw us off initially; if you remember the way the text for the Magic Books was stored, there was a clear separation between the diacritics and the words, with character value 0x66 used for ”. No such luck here. What the game actually does is use a secondary table where it defines where on screen the character meant to represent the diacritic will appear. This is why the example picture shows an "y" instead, as it replaced ” once we inserted our new font. As it turns out, it was quite near the previous table, smuggly waiting to be found between offsets 4B9BD and 4BA86. 

![Test Image 15](https://i.ibb.co/Wk9VD1H/DIACRITICS.png)

How does it work? Let's think back to Alice's dialogues. There are a total of 12 dialogues used during the game. 

```
4B9BD : 02 01 00 01 02 01 02 02 03 
4B9C6 : 02 01 00 01 02 03 04 04 05
4B9CF : 02 01 00 01 02 05 06 06 03
4B9D8 : 02 01 07 07 02 08 08 09 09
4B9E1 : 02 01 07 07 02 0A 0A 0B 01
4B9EA : 02 01 07 07 02 0C 05 0D 0B
4B9F3 : 02 01 0E 08 02 0F 0C 10 0A
4B9FC : 02 01 0E 08 02 11 08 12 05
4BA05 : 02 01 0E 08 02 13 0A 0D 0B
4BA0E : 02 02 14 0A 15 0D 02 16 09 17 0E
4BA19 : 02 02 18 0F 19 10 02 1A 11 1B 10
4BA24 : 04 01 1C 04 02 1D 12 1E 13 02 1F 14 20 0A 02 21 0A 22 05 40
```

The first 9 offsets are refering to the dialogues before the two final levels: 3 dialogues per sub-stage. The next 3 are used for the wordier characters, who turn out to be the King and Queen, present in the penultimate and final stages. As one can see, no reference to the 0x66 character value, or even 0x68, which would represent diacritic ゜. A brief series of tests revealed that, yes, these control the printing of the diacritics during dialogues. Experimenting revealed the values necessary to clear in order to get closer to a full English translation, and it was simply necessary to address these, writing them as 0x00 entries:

![Test Image 16](https://i.ibb.co/Rg7qJsW/DIACRITICS-2.png)

We had two other areas to contend with: the ending text, briefing players on Alice's success in vanquishing the demons, and the end credits. While not a novelty in regards to how text is stored in games, Alice's ending is nonetheless peculiar in that it's placed right after the intro text in the ROM. While the intro text block is comprised between offsets 35C05 and 35EC1, the ending follows right after, starting at offset 35EC2 and finishing at offset 35F8E.

As with the intro, the ending also makes use of some animations; while the intro shows the Rabbit's mouth opening and closing, the ending instead has Alice blink her eyes as she wakes up, and then goes back to sleep.

![Test Image 17](https://i.ibb.co/TKxb93w/Alice-12.png)

And much as with the code that handled the Rabbit's animation, so to does the ending make use of specific character codes to "animate" Alice's eyes:

![Test Image 18](https://i.ibb.co/18FFtzp/Alice-11.png)

The end credits had, to our advantage, partially been written with default character encodings. Which is to say, it used the same font for Alice's trademark message at the start, along with its "PUSH RUN BUTTON" message. If we didn't have access to filler's table, we could also make use of Mednafen's debugger once again, and build a table for the basic lettering in the game.

![Test Image 19](https://i.ibb.co/7YqLc8z/Alice-13.png)

The ending credits display a long list of developers involved in its production - but it also showcases the names of all characters, enemies and bosses in Alice, which remained in Japanese. After finding the beginning of the credits, where one can read "ALICE'S DREAMS'", it was easy to get an idea of their formatting. It uses both fonts in the game, and is located between offsets 574BF and 57C19.


## Insert a new font and reinsert the script

Nothing major to address here. Being small, the script was handled manually, something made easier by having to reduce the translation size. As far as font creation is concerned, the primary focus was to create something that suggested a dreamlike quality. I developed two fonts; however, one failed several readability tests and in hindsight, was larger and more cursive than necessary. The second attempt, inspired by The Legend of Zelda: Link's Awakening's italic but simpler lines, fared better and was used as the main font for our translation.

![Test Image 20](https://i.ibb.co/nPxsSSq/new-font.png)


## Localize and change the title screen logo

Care was placed into bringing forward a translation that felt like an official, overseas release. To this end, I was adamant about localizing the title and logo screen in a way that felt faithful to the original; while most people would go by the game's name alone, Fushigi no Yume no Alice actually ventures into several fairy tales, including not only Lewis Carroll stalwarts but also Pinocchio and the Little Red Riding Hood folk tale. Since the story involves denizens of these tales being corrupted or placed in harm's way, we decided on "The Fairytale Dreams of Alice", as it represented both the developer's intention and the game's content.

As mentioned before, MooZ's help was instrumental in finding, extracting and reinserting several of the game's graphics, specially the title screen.

![Test Image 21](https://i.ibb.co/d2LDQm8/TITLE.png)

*Original title screen on the left; our translation on the right.*


## Localize some of the graphics

![Test Image 23](https://i.ibb.co/tH52DKh/eek-bom.png)

Alice is a pretty standard videogame character, but other than using Magic Books that temporarily give her powers, she has two other basic attacks. One is jumping, which helps her navigate the levels and also land on enemies' heads (by far her most useful and damaging attack), and a scream ability that produces the word "イヤ" ("Iya", which can represent a shrill sound but also a rejection of something), that can hit enemies from afar. This had to be localized, along with an explosion effect caused by enemies that throw bombs at Alice, which display "BOM!" when exploding.

![Test Image 24](https://i.ibb.co/cY6SMt5/Alice-17.png)


## Timing issues

Changing the length of the intro meant that at some point, it would "overflow", placing its code over where the ending text once resided, and making the ending text code begin later. Alice doesn't read either data in a linear fashion; it uses a timing system that defines how long the intro lasts, and at what point the ending text begins and ends. Fortunately, MooZ was able to track down the code responsible for this. 
Those durations are both hard coded at 34017 and 340af.
```
; intro duration
8017: lda #$d3
8019: sta $2780
801C: lda #$10
801E: sta $2781

...

; ending duration
80af: lda #$80
80b1: sta $2780
80b4: lda #$05
80b6: sta $2781

```

The durations are expresed as frame counts. The intro thus lasts `0x10d3` frames and the ending `0x580`. As the PC Engine video output runs at 60 frames per seconds, a simple division will gives us `71` seconds for the intro and `23` seconds for the ending. 
In the end we needed to add `2` seconds to the intros. Adding `0x78` (`2*60`) to the original duration (`0x10d3`) did the trick.

## Find a good way to playtest changes

Any game undergoing a modification needs some method to quickly and accurately playtest it, ensuring the changes made are working out. Fortunately, Alice has two "cheat" codes, one producing access to a hidden Sound Test, accessbile at the Title Screen by pressing ```Button II, Right, Button I, Right, Button I, Down, Right, and Right``` - which surprised us with a message about a Soundtrack CD being available for the game, which we translated quickly. The other code allows users to skip to any level they so desire, with a small caveat.

To access it, it's necessary to press ```Down, Left, Button II, Up, Up, Button I, Right, and finally Select``` at the title screen, before it fades into the intro. Once that's done, players must press Button I the number of times corresponding to the level they wish to be whisked away to, minus 1. So if a player want to start at Stage 4, they must activate the Level Select cheat, then press Button I 3 times to start at Stage 4. After that, pressing the Run Button will start the game at the chosen level.

However, this is only halfway through Alice's madness. FACE and Sankindo's game is colorful and catchy, but is not particularly easy, due to Alice sliding rather than walking, and a somewhat enfuriating colision detection. To this end, we were fortunate to find an emulator cheat code that granted Alice partial invulnerability.

For Ootake, one of the emulators we tested our translation on, we used the code ```F83E00:97+```. For Mednafen and Magic Engine, we used the codes ```001F1E00 97``` and ```001F1E01 97```, which are inputted separately.

This code is a blessing, but has two drawbacks. One, Alice needs to be hit by something first (such as an enemy, an explosion or touching spikes) in order to trigger the effect, which will make her lose one health unit. Secondly, the effect is reset at the start of a sub-stage, meaning she needs to be hit again and subsequently, lose another health unit. But as long as players keep this in mind, that enemies killed may sometimes drop health units, and they also make use of the Red Magic Book to find hidden power-ups throughout the levels, they should be fine.


## Viva NEC!

And that's it for my part. I hope this information is useful for anyone looking to know how the translation for Fushigi no Yume no Alice was done.
