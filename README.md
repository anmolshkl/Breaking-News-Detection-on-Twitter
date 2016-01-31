# FYP16

## Data Set

DESCRIPTION
===========

The corpus consists of a total of 51,879,318 tweet IDs along with the
corresponding user screen names.  All tweets have to be processed by the FSD
system in the order that they appear in the tweet_ids file.  All the tweets
were obtained from Twitter's streaming API.  For evaluating FSD system
performance, 3034 tweets were tagged as being on-topic for one of 27 topics
(described below).  The format of relevance_judgments file is

tweet_id topic_id

tweet_id corresponds to one of the tweets in the tweets_ids file.  topic_id
identifies the topic that the tweet belongs to.  The first tweet in
relevance_judgments with a certain topic_id is the first story, and the rest
are non-first stories.

KNOWN ISSUES
============
The tweet_ids file may appear unsorted.  This is because when we encounter a
retweet, we take the original tweet's ID, not the retweet's ID.

Related to the previous point, some tweet IDs may appear more than once in
tweet_ids (e.g., if we have two tweets that retweet the same original tweet).

In the labeling process, topic 3 had a missed first story:
89497819701968897
This is NOT corrected in the relevance_judgments file (the first story in
relevance_judgments for topic 3 is still 89498478216089601).  Taking the
corrected first story into account will improve the absolute performance of FSD
systems, but it is highly unlikely that it will change their ranking.

TOPIC DESCRIPTIONS
==================

Topic 1: Death of Amy Winehouse
Topic 2: Space shuttle Atlantis lands safely, ending NASA's space shuttle program
Topic 3: Betty Ford dies
Topic 4: Richard Bowes, victim of London riots, dies in hospital
Topic 5: Flight Noar Linhas Aereas 4896 crashes, all 16 passengers dead
Topic 6: S&P downgrades US credit rating
Topic 7: US increases debt ceiling
Topic 8: Terrorist attack in Delhi
Topic 9: Earthquake in Virginia
Topic 10: Trevor Ellis (first victim of London riots) dies
Topic 11: Goran Hadzic, Yugoslavian war criminal, arrested
Topic 12: India and Bangladesh sign a peace pact
Topic 13: Plane carrying Russian hockey team Lokomotiv crashes, 44 dead
Topic 14: Explosion in French nuclear power plant Marcoule
Topic 15: NASA announces discovery of water on Mars
Topic 16: Google announces plans to buy Motorola Mobility
Topic 17: Car bomb explodes in Oslo, Norway
Topic 18: Gunman opens fire in children's camp on Utoya island, Norway
Topic 19: First artificial organ transplant
Topic 20: Petrol pipeline explosion in Kenya
Topic 21: Famine declared in Somalia
Topic 22: South Sudan declares independence
Topic 23: South Sudan becomes a UN member state
Topic 24: Three men die in riots in Birmingham
Topic 25: Riots break out in Tottenham
Topic 26: Rebels capture Tripoli international airport, Libya'
Topic 27: Ferry sinks in Zanzibar, around 200 dead

