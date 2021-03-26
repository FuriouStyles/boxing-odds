CREATE TABLE fights ( 
	fight_id              integer     ,
	red                  varchar(255)     ,
	blue                 varchar(255)     ,
	venue                varchar(255)     ,
	date                 date     ,
	time                 time     ,
	sex                  varchar(255)     ,
	title_fight          boolean     ,
	red_id               integer     ,
	blue_id              integer     , weight_class varchar(255)
 ) ;
CREATE TABLE fighter ( 
	br_id                integer     ,
	born                 date     ,
	division             varchar(255)     ,
	height_cm            integer     ,
	reach_cm             integer     ,
	nationality          varchar(255)     ,
	debut                date     ,
	stance               varchar(255)     ,
	wins                 integer     ,
	losses               integer     ,
	draws                integer     , name varchar(100)
 ) ;
CREATE TABLE fight_odds ( 
	Fighter              varchar(100)     ,
	Fivedimes            float(255,2)     ,
	WilliamH             float(255,2)     ,
	Bet365               float(255,2)     ,
	Bovada               float(255,2)     ,
	BookMaker            float(255,2)     ,
	BetDSI               float(255,2)     ,
	Intertops            float(255,2)     ,
	SportBet             float(255,2)     ,
	Pinnacle             float(255,2)     ,
	SportsInt            float(255,2)     ,
	BetOnline            float(255,2)     ,
	Sportsbook           float(255,2)     ,
	last_updated         timestamp     
 , fight_id varchar(255)) ;

CREATE TABLE model_pred ( 
	red_id               integer     ,
	blue_id              integer     ,
	fight_id             integer     ,
	red_win_prob         float(0,5)     ,
	red_lose_prob        float(0,5)     ,
	blue_win_prob        float(0,5)     ,
	blue_lose_prob       float(0,5)     ,
	red_draw_prob        float(0,5)     ,
	blue_draw_prob       float     ,
	blue_shap            long varchar     ,
	red_shap             long varchar       
 ) ;
