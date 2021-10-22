library("dplyr")
setwd("C:/Users/danie/PycharmProjects/pythonProject")
espn <- read.csv("2021_The_Federation_of_Bros_Position.csv", header = T)
espn <- espn[,-1]
espn[is.na(espn)] = 0
scores <- espn %>% filter(!Slot %in% c("Bench", "IR")) %>% 
  group_by(Week, Team) %>% 
  summarize(score = sum(Actual), projection = sum(Proj))

Schedule <- read.csv("2021_The_Federation_of_Bros_Schedule.csv", header = T)
Schedule <- Schedule[,-1]


home_join <- inner_join(Schedule, scores, by = c("weekid" = "Week", "homeid" = "Team"))
full6 <- inner_join(home_join, scores, by = c("weekid" = "Week", "awayid" = "Team"))
full6 <- full6 %>% filter(weekid ==6) %>% select(-c(gameid,homeptsactual,awayptsactual,score.x,score.y)) %>% mutate(favorite = if_else(projection.x > projection.y,homeid,awayid), 
                          favoritespread = if_else(projection.x > projection.y, projection.y-projection.x, projection.x-projection.y),
                          OUline = projection.x + projection.y)
full <- full6[1:35,]
full_schedule <- full %>%
  select(-c(score.x,score.y)) %>%
  rename(homeprojection = projection.x) %>%
  rename(awayprojection = projection.y) %>%
  mutate(favorite = if_else(homeprojection > awayprojection,homeid,awayid), 
         favoritespread = if_else(homeprojection > awayprojection, awayprojection-homeprojection, homeprojection-awayprojection),
         favoritespreadactual = if_else(homeprojection > awayprojection, awayptsactual-homeptsactual, homeptsactual-awayptsactual),
         cover = case_when(((homeprojection > awayprojection) & (homeptsactual + favoritespread > awayptsactual))|
                             ((awayprojection > homeprojection) & (awayptsactual + favoritespread < homeptsactual))  ~ homeid
                           ,TRUE ~ awayid),
         OU = if_else((homeptsactual+awayptsactual) > (homeprojection+awayprojection),"O","U"),
         OUline = homeprojection + awayprojection,
         OUactual = homeptsactual + awayptsactual)

home <- full_schedule %>% select(-c(awayid,awayptsactual,awayprojection)) %>% rename(teamid = homeid, pts = homeptsactual, projected = homeprojection)
away <- full_schedule %>% select(-c(homeid,homeptsactual,homeprojection)) %>% rename(teamid = awayid, pts = awayptsactual, projected = awayprojection)

teamdata <- rbind(home,away) %>% mutate(cover = ifelse(cover == teamid,1,0),
                                        OU = ifelse(OU == "O",1,0),
                                        favorite = ifelse(favorite==teamid,1,0),
                                        favoritecover = ifelse(favorite==1 & cover == 1,1,0),
                                        dogcover= ifelse(favorite == 0 & cover == 1,1,0),
                                        projptdiff = pts - projected,
                                        beatproj = ifelse(projptdiff > 0,1,0))

Leaguestats <- teamdata %>%
  summarize(Favoritecovers = sum(favoritecover),
            Dogcovers = sum(dogcover),
            Overs = sum(OU)/2, 
            Avgpts = mean(pts), 
            Avgproj = mean(projected), 
            AvgFavoriteSpread = mean(favoritespread), 
            Avgpointdiff = mean(abs(favoritespreadactual)),
            LargestMargin = max(abs(favoritespreadactual)),
            smallestMargin = min(abs(favoritespreadactual))
  )
Leaguestats

teamdata <- teamdata %>% group_by(weekid) %>% mutate(avgpts = mean(pts),quantile = ntile(pts,4), top3 = ifelse(quantile ==4,1,0), bottom4 = ifelse(quantile == 1,1,0))


Teamstats <- teamdata %>% group_by(teamid) %>%
  summarize(Favoritecovers = sum(favoritecover),
            Dogcovers = sum(dogcover),
            Favorite = sum(favorite),
            Totalcover = sum(dogcover) + sum(favoritecover),
            Overs = sum(OU), 
            Avgpts = mean(pts), 
            Avgproj = mean(projected), 
            beatprojection = sum(beatproj),
            top3pts = sum(top3),
            bottom4pts = sum(bottom4)
  )
Teamstats

                                            