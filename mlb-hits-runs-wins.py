#IMPORTING LIBRARIES

#To manipulate data, create dataframes
import pandas as pd
#For visualizations
import matplotlib.pyplot as plt
import seaborn as sns
#For calculating the R^2 value of a line
from scipy import stats


#SETTING THE COLOR SCHEME
#Using the MLB color scheme for the visualizations for this analysis.

#MLB logo color scheme
mlb_blue = '#002D72'
mlb_red = '#D50032'
mlb_colors = [mlb_blue, mlb_red]

#Create a MLB color palette
mlb_palette = sns.diverging_palette(258.7, 8.6, s=75, l=50, sep=1, n=30, center='light', as_cmap=False)


#LOADING DATA
#Reading the needed csv files
games_df = pd.read_csv('/kaggle/input/mlb-game-data/games.csv')
inning_df = pd.read_csv('/kaggle/input/mlb-game-data/inningHighlights.csv')

#Previewing games_df
games_df.head(5)

#Previewing inning_df
inning_df.head(5)


#MANIPULATING THE INNINGS DATA
#Using the innings data to determine:
#1. The first team that scored for each game
#2. The total number of hits for the home and away team for each game
#Each data point in the innings data represents each half inning.
#The data associated with each half inning needs to be assigned to the home and away team. The data also needs to be grouped and aggregated for each game.

#Grouping the innings data by game number
grouped_innings = inning_df.groupby('Game')

#Finding the inning where a team scored first for each game number
first_score = {}
for game, group in grouped_innings:
    #Finding the first inning with a number greater than 0
    first_inning = group.loc[group['Runs'] > 0, 'Inning'].iloc[0]
    first_score[game] = first_inning

#Summing the total hits for the home team for each game number
total_home_hits = {}
for game, group in grouped_innings:
    #If the inning starts with a B (bottom), that means it's the home team
    home_group = group[group['Inning'].str.contains('B')]
    #Calculating the total score by summing the hits for all innings in each game
    total_hits = home_group['Hits'].sum()
    total_home_hits[game] = total_hits

#Summing the total hits for the away team for each game number
total_away_hits = {}
for game, group in grouped_innings:
    #If the inning starts with a T (top), that means it's the away team
    away_group = group[group['Inning'].str.contains('T')]
    #Calculating the total score by summing the hits for all innings in each game
    total_hits = away_group['Hits'].sum()
    total_away_hits[game] = total_hits


#MANIPULATING THE GAMES DATA
#Using the games data to determine the winner of each game. Adding the innings data from above to:
#1. Assign the total number of home and away team hits for each game and determine which team had the most hits for each game
#2. Determine which team scored first for each game

#Only want to see the game, teams and scores
games = games_df.loc[:,['Game', 'away', 'away-score', 'home', 'home-score']]

#Finding the winning and losing team for each game
away_team = games['away']
away_score = games['away-score']
home_team = games['home']
home_score = games['home-score']
winner_list = []
loser_list = []
for a, a_s, h, h_s in zip(away_team, away_score, home_team, home_score):
    if a_s > h_s:
        winner_list.append(a)
        loser_list.append(h)
    elif a_s < h_s:
        winner_list.append(h)
        loser_list.append(a)
    else:
        winner_list.append('tie')
        loser_list.append('tie')

#Adding the new winner and loser column and data to games
#This is the winning team of each game
games['winner'] = winner_list
#This is the losing team of each game
games['loser'] = loser_list

#Adding the new away_hits column and data to games
#These are the total hits for the away team for each game
games_num = games['Game']
away_hit_list = []
for i in games_num:
    away_hit_list.append(total_away_hits.get(i))
games['away_hits'] = away_hit_list

#Adding the new home_hits column and data to games
#These are the total hits for the home team for each game
home_hit_list = []
for i in games_num:
    home_hit_list.append(total_home_hits.get(i))
games['home_hits'] = home_hit_list

#Adding the new first_score_inning column and data to games
#This is the first inning where someone scores in each game
first_score_list = []
for i in games_num:
    first_score_list.append(first_score.get(i))
games['first_score_inning'] = first_score_list

#Adding the new first_score_team column and data to games
#This is the team that scored first (i.e.,first inning where someone scores) in each game
first_score_team = []
for f, a, h in zip(games['first_score_inning'], away_team, home_team):
    if 'T' in str(f):
        first_score_team.append(a)
    else:
        first_score_team.append(h)
games['first_score_team'] = first_score_team

#Adding the new most_hits_team column and data to games
#This determines which team had the most hits for each game
most_hits_team = []
for a, a_h, h, h_h in zip(away_team, games['away_hits'], home_team, games['home_hits']):
    if a_h > h_h:
        most_hits_team.append(a)
    elif a_h < h_h:
        most_hits_team.append(h)
    else:
        most_hits_team.append('tie')
games['most_hits_team'] = most_hits_team


#CREATING FIRST SCORES AND MOST HITS DATA
#Combining the innings and games data to determine whether:
#1. The winning team had the most hits
#2. The winning team scored first

#Adding the new winner_first_scorer column and data to games
#This determines whether the first team that scored was the winner
winner_first_scorer = []
for w, f in zip(games['winner'], games['first_score_team']):
    if w == f:
        winner_first_scorer.append(True)
    else:
        winner_first_scorer.append(False)
games['winner_first_scorer'] = winner_first_scorer

#Adding the new winner_most_hits column and data to games
#This determines whether the first team that scored was the winner
winner_most_hits = []
for w, h in zip(games['winner'], games['most_hits_team']):
    if w == h:
        winner_most_hits.append(True)
    else:
        winner_most_hits.append(False)
games['winner_most_hits'] = winner_most_hits

#Excluding data from AL and tie
#AL is not a team name
#Tie means no one one the game and with this analysis we just want to look at wins and losses
games = games[~games['winner'].isin(['AL', 'tie'])]

#Previewing the new games data
games.head()


#DID TEAMS THAT WON HAVE THE MOST HITS?
#Determining the number and percentage of games where the teams that won had the highest number of hits and visualizing the results.

#Whether winners had the most hits
count_hit_wins = games['winner_most_hits'].value_counts()

#Total games played
total_count_hit_wins = count_hit_wins.sum()

#Viewing the results
pd.DataFrame(data=count_hit_wins)

#Visualizing this data, creating a bar chart
plt.bar(['True', 'False'], count_hit_wins.values, color = mlb_colors, edgecolor='black')

#Specifying labels and title
plt.xlabel('Winner Had the Most Hits', fontweight="bold")
plt.ylabel('Total Games Played', fontweight="bold")
plt.title('Did Winners Have the Most Hits?', fontweight="bold", fontsize="16", pad=15)

#Adding the percentages of True and False to the chart
for i, count in enumerate(count_hit_wins.values):
    percent = count / total_count_hit_wins * 100
    plt.text(i, count, f'{percent:.2f}%', ha='center', va='bottom', fontweight="bold")

#Displaying the plot
plt.show()

#Comparing wins based on whether the team scored first or had the most hits, there were more instances where the winners had the highest number of hits.
#Let's focus on hits for the rest of this analysis!


#ARE RESULTS DIFFERENT FOR EACH TEAM?
#Determining whether winners who had the highest number of hits were different for each team.

#Wins and losses for each team
#First, let's first look at the overall wins and losses record for each team.

#Creating a new dataframe with the winners and losers
win_loss_data = {'wins': games['winner'], 'losses': games['loser']}
win_loss_data_df = pd.DataFrame(win_loss_data)

#Counting the number of wins and losses per team
win_counts = win_loss_data_df['wins'].value_counts()
loss_counts = win_loss_data_df['losses'].value_counts()

#Calculating and appending the percent wins for each team
percent_wins = []
for w, l in zip(win_counts, loss_counts):
    percent_wins.append(round(w/(w+l) * 100, 2))

#Calculating and appending the percent losses for each team
percent_loss = []
for w, l in zip(win_counts, loss_counts):
    percent_loss.append(round(l/(w+l) * 100, 2))

#Creating a new dataframe combining the counts and percentages
team_win_loss_records = pd.DataFrame({
    'wins': win_counts,
    'losses': loss_counts,
    'percent_wins': percent_wins,
    'percent_losses': percent_loss
})

#Sorting the combined_data dataframe by percent_wins in descending order
team_win_loss_records = team_win_loss_records.sort_values('percent_wins', ascending=False)

#Resetting the index and renaming the index column as 'team'
team_win_loss_records = team_win_loss_records.reset_index().rename(columns={'index':'team'})

#Displaying the combined data
print(team_win_loss_records)

#Games where the winner had the most hits by each team

#Whether the winner had the most hits, grouping by team
#Resetting the index so the final column is 'counts'
count_most_hits_team = games.groupby('winner')['winner_most_hits'].value_counts().reset_index(name='counts')

# Renaming the 'winner' column to 'team'
count_most_hits_team = count_most_hits_team.rename(columns={'winner': 'team'})

#Viewing the results
pd.DataFrame(data=count_most_hits_team)

# Merging the dataframe for total wins above and wins based on having the total number of hits
team_percents = count_most_hits_team[count_most_hits_team['winner_most_hits'] == True][['team','counts']].merge(team_win_loss_records[['team','wins']], on='team')

#Calculating the percentage of true values for each team
team_percents['percent_true'] = team_percents['counts'] / team_percents['wins'] * 100

#Sorting the dataframe by the percentage of true values in descending order
team_percents = team_percents.sort_values('percent_true', ascending=False)

#Rounding to two decimal places
team_percents = team_percents.round(decimals=2)

#Viewing the results, only want to see the team and percent column
print(team_percents[['team', 'percent_true']])


#BIVARIATE ANALYSIS
#Using a bivariate analysis to understand the correlation between wins overall and wins due to having the highest number of hits. In other words, are the teams that have more wins due to having the highest number of hits more likely to have more wins overall?

#Creating a new dataframe with overall wins and wins due to the most hits
combined_data = pd.DataFrame(team_percents, columns=['team', 'percent_true'])

#Renaming the column 'percent_true to 'percent_wins_most_hits'
combined_data = combined_data.rename(columns={'percent_true': 'percent_wins_most_hits'})

#Adding the percent_wins from the overall wins/loss record into the dataframe
wins_team = []
for i in team_win_loss_records['percent_wins']:
    wins_team.append(i)
combined_data['percent_wins'] = wins_team

#Viewing the results
print(combined_data)

#Calculating statistical data for combined_data
combined_data.describe()

#Visualizing the relationship between wins overall and wins due to having the most hits
sns.pairplot(combined_data)
plt.show()

#Visualizing by team
graph = sns.scatterplot(x="percent_wins_most_hits", y="percent_wins", data=combined_data, hue='team', legend=True, s=100, palette=mlb_palette)

#Adding a trendline
sns.regplot(x="percent_wins_most_hits", y="percent_wins", data=combined_data, scatter=False)

#Customizing x and y axis labels
graph.set(xlabel='Percent of Wins from Most Hits', ylabel='Percent of Wins')

#Adjusting the size of the legend
plt.legend(loc="center left", bbox_to_anchor=(1, 0.6), prop={'size': 8})

#Adding a title
plt.title("Wins vs Wins Due to Most Hits", fontweight="bold")

plt.show()

# Calculating the R^2 value of the line
x = combined_data["percent_wins_most_hits"]
y = combined_data["percent_wins"]
slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
r_squared = r_value**2
r_squared = r_squared.round(3)

print(r_squared)

#Calculating the correlation of Percent of Wins From Most Hits and Percent of Wins

# Pearson's r correlation
r = x.corr(y)
rounded_r = round(r, 3)

print(rounded_r)

# Spearman's rho correlation
r = x.corr(y, method='spearman')
rounded_r = round(r, 3)

print(rounded_r)

# Kendall's tau correlation
r = x.corr(y, method='kendall')
rounded_r = round(r, 3)

print(rounded_r)
