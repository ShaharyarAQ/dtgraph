from dtgraph.scenarios.scenario import Scenario

class Football(Scenario):
    @staticmethod
    def load(graph, size=None):
        script = """
            // ══════════════════════════════════════════════════════
            //  NODE TYPES: Player, Club, League, Manager, Season,
            //              Trophy, Nation, Agent
            // ══════════════════════════════════════════════════════

            // ─── NATIONS ──────────────────────────────────────────
            CREATE (England:Nation   {name:'England',   confederation:'UEFA', population:56000000})
            CREATE (Spain:Nation     {name:'Spain',     confederation:'UEFA', population:47000000})
            CREATE (Germany:Nation   {name:'Germany',   confederation:'UEFA', population:83000000})
            CREATE (France:Nation    {name:'France',    confederation:'UEFA', population:68000000})
            CREATE (Brazil:Nation    {name:'Brazil',    confederation:'CONMEBOL', population:215000000})
            CREATE (Argentina:Nation {name:'Argentina', confederation:'CONMEBOL', population:45000000})
            CREATE (Portugal:Nation  {name:'Portugal',  confederation:'UEFA', population:10000000})
            CREATE (Netherlands:Nation {name:'Netherlands', confederation:'UEFA', population:17000000})

            // ─── LEAGUES ──────────────────────────────────────────
            CREATE (PL:League   {name:'Premier League', country:'England', founded:1992, prestige:98, prize_money_m:2500})
            CREATE (LL:League   {name:'La Liga',        country:'Spain',   founded:1929, prestige:95, prize_money_m:1800})
            CREATE (BL:League   {name:'Bundesliga',     country:'Germany', founded:1963, prestige:90, prize_money_m:1400})
            CREATE (SA:League   {name:'Serie A',        country:'Italy',   founded:1929, prestige:88, prize_money_m:1200})
            CREATE (UCL:League  {name:'UEFA Champions League', country:'Europe', founded:1955, prestige:100, prize_money_m:2000})

            // ─── CLUBS ────────────────────────────────────────────
            CREATE (ManCity:Club    {name:'Manchester City',  founded:1880, value_m:5100, wage_bill_m:350, stadium:'Etihad Stadium',    capacity:55097})
            CREATE (Liverpool:Club  {name:'Liverpool FC',     founded:1892, value_m:4700, wage_bill_m:320, stadium:'Anfield',            capacity:61276})
            CREATE (RealMadrid:Club {name:'Real Madrid',      founded:1902, value_m:6100, wage_bill_m:420, stadium:'Santiago Bernabéu',  capacity:81044})
            CREATE (Barcelona:Club  {name:'FC Barcelona',     founded:1899, value_m:4800, wage_bill_m:390, stadium:'Camp Nou',           capacity:99354})
            CREATE (BayernM:Club    {name:'Bayern Munich',    founded:1900, value_m:4500, wage_bill_m:340, stadium:'Allianz Arena',      capacity:75024})
            CREATE (PSG:Club        {name:'Paris Saint-Germain', founded:1970, value_m:4200, wage_bill_m:400, stadium:'Parc des Princes', capacity:47929})
            CREATE (ManUnited:Club  {name:'Manchester United',founded:1878, value_m:3900, wage_bill_m:290, stadium:'Old Trafford',       capacity:74310})
            CREATE (Juventus:Club   {name:'Juventus FC',      founded:1897, value_m:2100, wage_bill_m:210, stadium:'Allianz Stadium',    capacity:41507})
            CREATE (Arsenal:Club    {name:'Arsenal FC',       founded:1886, value_m:3200, wage_bill_m:270, stadium:'Emirates Stadium',   capacity:60704})
            CREATE (Atletico:Club   {name:'Atletico Madrid',  founded:1903, value_m:2400, wage_bill_m:230, stadium:'Civitas Metropolitano', capacity:68456})
            CREATE (Chelsea:Club    {name:'Chelsea FC',       founded:1905, value_m:2900, wage_bill_m:280, stadium:'Stamford Bridge',   capacity:40341})
            CREATE (Dortmund:Club   {name:'Borussia Dortmund',founded:1909, value_m:1900, wage_bill_m:190, stadium:'Signal Iduna Park',  capacity:81365})
            CREATE (ACMilan:Club    {name:'AC Milan',          founded:1899, value_m:3100, wage_bill_m:250, stadium:'San Siro',           capacity:80018})

            // ─── CLUB COMPETES IN LEAGUE ───────────────────────────
            CREATE
            (ManCity)-[:IN_LEAGUE    {since:2002, current:true}]->(PL),
            (Liverpool)-[:IN_LEAGUE  {since:1962, current:true}]->(PL),
            (ManUnited)-[:IN_LEAGUE  {since:1992, current:true}]->(PL),
            (Arsenal)-[:IN_LEAGUE    {since:1992, current:true}]->(PL),
            (Chelsea)-[:IN_LEAGUE    {since:1992, current:true}]->(PL),
            (RealMadrid)-[:IN_LEAGUE {since:1929, current:true}]->(LL),
            (Barcelona)-[:IN_LEAGUE  {since:1929, current:true}]->(LL),
            (Atletico)-[:IN_LEAGUE   {since:1934, current:true}]->(LL),
            (BayernM)-[:IN_LEAGUE    {since:1965, current:true}]->(BL),
            (Dortmund)-[:IN_LEAGUE   {since:1981, current:true}]->(BL),
            (Juventus)-[:IN_LEAGUE   {since:1929, current:true}]->(SA),
            (PSG)-[:IN_LEAGUE        {since:1974, current:true}]->(LL)

            // ─── CLUB RIVALS ───────────────────────────────────────
            CREATE
            (ManCity)-[:RIVALS_WITH    {rivalry_name:'Manchester Derby',    intensity:9}]->(ManUnited),
            (ManUnited)-[:RIVALS_WITH  {rivalry_name:'Manchester Derby',    intensity:9}]->(ManCity),
            (Liverpool)-[:RIVALS_WITH  {rivalry_name:'North West Derby',    intensity:8}]->(ManUnited),
            (ManUnited)-[:RIVALS_WITH  {rivalry_name:'North West Derby',    intensity:8}]->(Liverpool),
            (RealMadrid)-[:RIVALS_WITH {rivalry_name:'El Clásico',          intensity:10}]->(Barcelona),
            (Barcelona)-[:RIVALS_WITH  {rivalry_name:'El Clásico',          intensity:10}]->(RealMadrid),
            (Atletico)-[:RIVALS_WITH   {rivalry_name:'Madrid Derby',        intensity:8}]->(RealMadrid),
            (RealMadrid)-[:RIVALS_WITH {rivalry_name:'Madrid Derby',        intensity:8}]->(Atletico),
            (BayernM)-[:RIVALS_WITH    {rivalry_name:'Der Klassiker',       intensity:9}]->(Dortmund),
            (Dortmund)-[:RIVALS_WITH   {rivalry_name:'Der Klassiker',       intensity:9}]->(BayernM),
            (Arsenal)-[:RIVALS_WITH    {rivalry_name:'North London Derby',  intensity:8}]->(Chelsea)

            // ─── SEASONS ──────────────────────────────────────────
            CREATE (S2021:Season {year:'2021-22', start_date:'2021-08-14', end_date:'2022-05-22'})
            CREATE (S2022:Season {year:'2022-23', start_date:'2022-08-06', end_date:'2023-05-28'})
            CREATE (S2023:Season {year:'2023-24', start_date:'2023-08-12', end_date:'2024-05-19'})

            // ─── CLUB WON LEAGUE IN SEASON ─────────────────────────
            CREATE
            (ManCity)-[:WON_LEAGUE  {points:93, goals_for:99, goals_against:26}]->(S2021),
            (ManCity)-[:WON_LEAGUE  {points:89, goals_for:94, goals_against:33}]->(S2022),
            (ManCity)-[:WON_LEAGUE  {points:91, goals_for:96, goals_against:34}]->(S2023),
            (RealMadrid)-[:WON_LEAGUE {points:86, goals_for:80, goals_against:31}]->(S2021),
            (Barcelona)-[:WON_LEAGUE  {points:88, goals_for:70, goals_against:20}]->(S2022),
            (BayernM)-[:WON_LEAGUE    {points:77, goals_for:92, goals_against:38}]->(S2021),
            (BayernM)-[:WON_LEAGUE    {points:71, goals_for:92, goals_against:39}]->(S2022),
            (PSG)-[:WON_LEAGUE        {points:86, goals_for:89, goals_against:40}]->(S2021),
            (PSG)-[:WON_LEAGUE        {points:85, goals_for:95, goals_against:36}]->(S2022)

            // ─── TROPHIES ─────────────────────────────────────────
            CREATE (UCLTrophy:Trophy   {name:'UEFA Champions League', tier:'Continental', prize_m:20})
            CREATE (PLTrophy:Trophy    {name:'Premier League Title',  tier:'Domestic',    prize_m:5})
            CREATE (LLTrophy:Trophy    {name:'La Liga Title',         tier:'Domestic',    prize_m:4})
            CREATE (BLTrophy:Trophy    {name:'Bundesliga Title',      tier:'Domestic',    prize_m:3})
            CREATE (FACup:Trophy       {name:'FA Cup',                tier:'Cup',         prize_m:2})
            CREATE (BallonDor:Trophy   {name:"Ballon d'Or",           tier:'Individual',  prize_m:0})
            CREATE (GoldenBoot:Trophy  {name:'Golden Boot',           tier:'Individual',  prize_m:0})

            // ─── MANAGERS ─────────────────────────────────────────
            CREATE (Guardiola:Manager  {name:'Pep Guardiola',    born:1971, nationality:'Spanish',   style:'Tiki-taka / Positional'})
            CREATE (Klopp:Manager      {name:'Jürgen Klopp',     born:1967, nationality:'German',    style:'Gegenpressing'})
            CREATE (Ancelotti:Manager  {name:'Carlo Ancelotti',  born:1959, nationality:'Italian',   style:'Pragmatic / Flexible'})
            CREATE (Xavi:Manager       {name:'Xavi Hernández',   born:1980, nationality:'Spanish',   style:'Positional / Possession'})
            CREATE (Tuchel:Manager     {name:'Thomas Tuchel',    born:1973, nationality:'German',    style:'High Press / Gegenpressing'})
            CREATE (Simeone:Manager    {name:'Diego Simeone',    born:1970, nationality:'Argentine', style:'Low Block / Counter'})
            CREATE (TenHag:Manager     {name:'Erik ten Hag',     born:1970, nationality:'Dutch',     style:'Positional / Press'})
            CREATE (Arteta:Manager     {name:'Mikel Arteta',     born:1982, nationality:'Spanish',   style:'High Press / Positional'})

            // ─── MANAGER COACHED CLUB ──────────────────────────────
            // current stints
            CREATE
            (Guardiola)-[:MANAGED {from_year:2016, to_year:null,  current:true,  trophies_won:14}]->(ManCity),
            (Klopp)-[:MANAGED     {from_year:2015, to_year:2024,  current:false, trophies_won:7}]->(Liverpool),
            (Ancelotti)-[:MANAGED {from_year:2021, to_year:null,  current:true,  trophies_won:5}]->(RealMadrid),
            (Xavi)-[:MANAGED      {from_year:2021, to_year:2024,  current:false, trophies_won:3}]->(Barcelona),
            (Tuchel)-[:MANAGED    {from_year:2023, to_year:null,  current:true,  trophies_won:1}]->(BayernM),
            (Simeone)-[:MANAGED   {from_year:2011, to_year:null,  current:true,  trophies_won:11}]->(Atletico),
            (TenHag)-[:MANAGED    {from_year:2022, to_year:null,  current:true,  trophies_won:2}]->(ManUnited),
            (Arteta)-[:MANAGED    {from_year:2019, to_year:null,  current:true,  trophies_won:3}]->(Arsenal)

            // historical stints — same manager, different club
            CREATE
            (Guardiola)-[:MANAGED {from_year:2008, to_year:2012, current:false, trophies_won:14}]->(Barcelona),
            (Guardiola)-[:MANAGED {from_year:2013, to_year:2016, current:false, trophies_won:7}]->(BayernM),
            (Tuchel)-[:MANAGED    {from_year:2021, to_year:2023, current:false, trophies_won:2}]->(Chelsea),
            (Klopp)-[:MANAGED     {from_year:2008, to_year:2015, current:false, trophies_won:2}]->(Dortmund),
            (Ancelotti)-[:MANAGED {from_year:2013, to_year:2015, current:false, trophies_won:2}]->(RealMadrid),
            (Ancelotti)-[:MANAGED {from_year:2009, to_year:2011, current:false, trophies_won:1}]->(Chelsea),
            (Ancelotti)-[:MANAGED {from_year:2016, to_year:2018, current:false, trophies_won:0}]->(BayernM)

            // ─── MANAGER NATIONALITY ──────────────────────────────
            CREATE
            (Guardiola)-[:REPRESENTS]->(Spain),
            (Klopp)-[:REPRESENTS]->(Germany),
            (Ancelotti)-[:REPRESENTS]->(France),
            (Tuchel)-[:REPRESENTS]->(Germany),
            (Simeone)-[:REPRESENTS]->(Argentina),
            (TenHag)-[:REPRESENTS]->(Netherlands),
            (Arteta)-[:REPRESENTS]->(Spain)

            // ─── AGENTS ───────────────────────────────────────────
            CREATE (Mendes:Agent    {name:'Jorge Mendes',   agency:'Gestifute',   clients:45, founded:1996})
            CREATE (Raiola:Agent    {name:'Mino Raiola',    agency:'SEM',         clients:30, founded:1993})
            CREATE (Barnett:Agent   {name:'Jonathan Barnett', agency:'Stellar Group', clients:60, founded:2001})

            // ─── PLAYERS ──────────────────────────────────────────
            CREATE (Haaland:Player  {name:'Erling Haaland',  born:2000, position:'ST',  nationality:'Norwegian', market_value_m:200, goals_career:250, caps:40})
            CREATE (Salah:Player    {name:'Mohamed Salah',   born:1992, position:'RW',  nationality:'Egyptian',  market_value_m:60,  goals_career:330, caps:95})
            CREATE (Vinicius:Player {name:'Vinicius Jr.',    born:2000, position:'LW',  nationality:'Brazilian', market_value_m:180, goals_career:120, caps:30})
            CREATE (Mbappe:Player   {name:'Kylian Mbappé',   born:1998, position:'ST',  nationality:'French',    market_value_m:180, goals_career:310, caps:80})
            CREATE (Bellingham:Player {name:'Jude Bellingham',born:2003, position:'CM', nationality:'English',   market_value_m:200, goals_career:80,  caps:35})
            CREATE (Pedri:Player    {name:'Pedri',           born:2002, position:'CM',  nationality:'Spanish',   market_value_m:100, goals_career:45,  caps:28})
            CREATE (Rodri:Player    {name:'Rodri',           born:1996, position:'CDM', nationality:'Spanish',   market_value_m:150, goals_career:40,  caps:55})
            CREATE (Alisson:Player  {name:'Alisson Becker',  born:1992, position:'GK',  nationality:'Brazilian', market_value_m:50,  goals_career:2,   caps:75})
            CREATE (VanDijk:Player  {name:'Virgil van Dijk', born:1991, position:'CB',  nationality:'Dutch',     market_value_m:50,  goals_career:50,  caps:65})
            CREATE (Saka:Player     {name:'Bukayo Saka',     born:2001, position:'RW',  nationality:'English',   market_value_m:150, goals_career:90,  caps:40})
            CREATE (Leao:Player     {name:'Rafael Leão',     born:2001, position:'LW',  nationality:'Portuguese',market_value_m:90,  goals_career:80,  caps:25})
            CREATE (Kroos:Player    {name:'Toni Kroos',      born:1990, position:'CM',  nationality:'German',    market_value_m:20,  goals_career:120, caps:106})
            CREATE (Neuer:Player    {name:'Manuel Neuer',    born:1986, position:'GK',  nationality:'German',    market_value_m:10,  goals_career:0,   caps:124})
            CREATE (Kane:Player     {name:'Harry Kane',      born:1993, position:'ST',  nationality:'English',   market_value_m:100, goals_career:380, caps:91})
            CREATE (Griezmann:Player{name:'Antoine Griezmann',born:1991, position:'AM', nationality:'French',    market_value_m:35,  goals_career:310, caps:130})
            CREATE (Stones:Player   {name:'John Stones',     born:1994, position:'CB',  nationality:'English',   market_value_m:45,  goals_career:20,  caps:75})

            // ─── PLAYER CURRENTLY AT CLUB ─────────────────────────
            CREATE
            (Haaland)-[:PLAYS_FOR    {since:2022, shirt_number:9,  weekly_wage_k:375, contract_until:2027}]->(ManCity),
            (Salah)-[:PLAYS_FOR      {since:2017, shirt_number:11, weekly_wage_k:350, contract_until:2025}]->(Liverpool),
            (Vinicius)-[:PLAYS_FOR   {since:2018, shirt_number:7,  weekly_wage_k:300, contract_until:2027}]->(RealMadrid),
            (Mbappe)-[:PLAYS_FOR     {since:2024, shirt_number:9,  weekly_wage_k:900, contract_until:2029}]->(RealMadrid),
            (Bellingham)-[:PLAYS_FOR {since:2023, shirt_number:5,  weekly_wage_k:400, contract_until:2029}]->(RealMadrid),
            (Pedri)-[:PLAYS_FOR      {since:2020, shirt_number:8,  weekly_wage_k:200, contract_until:2026}]->(Barcelona),
            (Rodri)-[:PLAYS_FOR      {since:2019, shirt_number:16, weekly_wage_k:250, contract_until:2027}]->(ManCity),
            (Alisson)-[:PLAYS_FOR    {since:2018, shirt_number:1,  weekly_wage_k:150, contract_until:2027}]->(Liverpool),
            (VanDijk)-[:PLAYS_FOR    {since:2018, shirt_number:4,  weekly_wage_k:220, contract_until:2025}]->(Liverpool),
            (Saka)-[:PLAYS_FOR       {since:2018, shirt_number:7,  weekly_wage_k:300, contract_until:2027}]->(Arsenal),
            (Leao)-[:PLAYS_FOR       {since:2019, shirt_number:10, weekly_wage_k:180, contract_until:2028}]->(ACMilan),
            (Kroos)-[:PLAYS_FOR      {since:2014, shirt_number:8,  weekly_wage_k:200, contract_until:2025}]->(RealMadrid),
            (Neuer)-[:PLAYS_FOR      {since:2011, shirt_number:1,  weekly_wage_k:180, contract_until:2025}]->(BayernM),
            (Kane)-[:PLAYS_FOR       {since:2023, shirt_number:9,  weekly_wage_k:400, contract_until:2027}]->(BayernM),
            (Griezmann)-[:PLAYS_FOR  {since:2021, shirt_number:7,  weekly_wage_k:250, contract_until:2026}]->(Atletico),
            (Stones)-[:PLAYS_FOR     {since:2016, shirt_number:5,  weekly_wage_k:180, contract_until:2026}]->(ManCity)

            // ─── PLAYER NATIONALITY ───────────────────────────────
            CREATE
            (Vinicius)-[:REPRESENTS]->(Brazil),
            (Alisson)-[:REPRESENTS]->(Brazil),
            (Mbappe)-[:REPRESENTS]->(France),
            (Griezmann)-[:REPRESENTS]->(France),
            (Rodri)-[:REPRESENTS]->(Spain),
            (Pedri)-[:REPRESENTS]->(Spain),
            (Bellingham)-[:REPRESENTS]->(England),
            (Saka)-[:REPRESENTS]->(England),
            (Kane)-[:REPRESENTS]->(England),
            (Stones)-[:REPRESENTS]->(England),
            (VanDijk)-[:REPRESENTS]->(Netherlands),
            (Kroos)-[:REPRESENTS]->(Germany),
            (Neuer)-[:REPRESENTS]->(Germany)

            // ─── AGENT REPRESENTS PLAYER ──────────────────────────
            CREATE
            (Mendes)-[:REPRESENTS_PLAYER  {commission_pct:5}]->(Mbappe),
            (Mendes)-[:REPRESENTS_PLAYER  {commission_pct:5}]->(Leao),
            (Mendes)-[:REPRESENTS_PLAYER  {commission_pct:5}]->(Vinicius),
            (Barnett)-[:REPRESENTS_PLAYER {commission_pct:4}]->(Bellingham),
            (Barnett)-[:REPRESENTS_PLAYER {commission_pct:4}]->(Saka),
            (Barnett)-[:REPRESENTS_PLAYER {commission_pct:4}]->(VanDijk),
            (Raiola)-[:REPRESENTS_PLAYER  {commission_pct:5}]->(Haaland),
            (Raiola)-[:REPRESENTS_PLAYER  {commission_pct:5}]->(Kane)
            // ─── PLAYER WON TROPHY ────────────────────────────────
            CREATE
            (Haaland)-[:WON_TROPHY  {year:2023, with_club:'Manchester City', goals_in_competition:12}]->(UCLTrophy),
            (Haaland)-[:WON_TROPHY  {year:2022, with_club:'Manchester City', goals_in_competition:36}]->(PLTrophy),
            (Haaland)-[:WON_TROPHY  {year:2023, with_club:'Manchester City', goals_in_competition:36}]->(PLTrophy),
            (Haaland)-[:WON_TROPHY  {year:2024, with_club:'Manchester City', goals_in_competition:27}]->(PLTrophy),
            (Haaland)-[:WON_TROPHY  {year:2023, with_club:'Manchester City', goals_in_competition:36}]->(GoldenBoot),
            (Rodri)-[:WON_TROPHY    {year:2023, with_club:'Manchester City', goals_in_competition:3}]->(UCLTrophy),
            (Rodri)-[:WON_TROPHY    {year:2024, with_club:'Spain',           goals_in_competition:2}]->(BallonDor),
            (Salah)-[:WON_TROPHY    {year:2019, with_club:'Liverpool',       goals_in_competition:7}]->(UCLTrophy),
            (Alisson)-[:WON_TROPHY  {year:2019, with_club:'Liverpool',       goals_in_competition:0}]->(UCLTrophy),
            (VanDijk)-[:WON_TROPHY  {year:2019, with_club:'Liverpool',       goals_in_competition:3}]->(UCLTrophy),
            (Vinicius)-[:WON_TROPHY {year:2022, with_club:'Real Madrid',     goals_in_competition:8}]->(UCLTrophy),
            (Vinicius)-[:WON_TROPHY {year:2024, with_club:'Real Madrid',     goals_in_competition:6}]->(UCLTrophy),
            (Kroos)-[:WON_TROPHY    {year:2022, with_club:'Real Madrid',     goals_in_competition:3}]->(UCLTrophy),
            (Kroos)-[:WON_TROPHY    {year:2024, with_club:'Real Madrid',     goals_in_competition:2}]->(UCLTrophy),
            (Bellingham)-[:WON_TROPHY {year:2024, with_club:'Real Madrid',   goals_in_competition:9}]->(UCLTrophy),
            (Mbappe)-[:WON_TROPHY   {year:2022, with_club:'PSG',             goals_in_competition:5}]->(GoldenBoot),
            (Kane)-[:WON_TROPHY     {year:2024, with_club:'Bayern Munich',   goals_in_competition:36}]->(BLTrophy),
            (Kane)-[:WON_TROPHY     {year:2024, with_club:'Bayern Munich',   goals_in_competition:44}]->(GoldenBoot),
            (Griezmann)-[:WON_TROPHY {year:2021, with_club:'Atletico Madrid',goals_in_competition:8}]->(LLTrophy),
            (Saka)-[:WON_TROPHY     {year:2020, with_club:'Arsenal',         goals_in_competition:4}]->(FACup),
            (Saka)-[:WON_TROPHY     {year:2023, with_club:'Arsenal',         goals_in_competition:14}]->(FACup)

            // ─── CLUB WON TROPHY ──────────────────────────────────
            CREATE
            (ManCity)-[:WON_TROPHY   {year:2023, season:'2022-23', manager:'Pep Guardiola'}]->(UCLTrophy),
            (ManCity)-[:WON_TROPHY   {year:2019, season:'2018-19', manager:'Pep Guardiola'}]->(PLTrophy),
            (ManCity)-[:WON_TROPHY   {year:2022, season:'2021-22', manager:'Pep Guardiola'}]->(PLTrophy),
            (ManCity)-[:WON_TROPHY   {year:2023, season:'2022-23', manager:'Pep Guardiola'}]->(PLTrophy),
            (Liverpool)-[:WON_TROPHY {year:2019, season:'2018-19', manager:'Jürgen Klopp'}]->(UCLTrophy),
            (Liverpool)-[:WON_TROPHY {year:2020, season:'2019-20', manager:'Jürgen Klopp'}]->(PLTrophy),
            (RealMadrid)-[:WON_TROPHY {year:2022, season:'2021-22', manager:'Carlo Ancelotti'}]->(UCLTrophy),
            (RealMadrid)-[:WON_TROPHY {year:2024, season:'2023-24', manager:'Carlo Ancelotti'}]->(UCLTrophy),
            (BayernM)-[:WON_TROPHY   {year:2020, season:'2019-20', manager:'Hansi Flick'}]->(UCLTrophy),
            (Arsenal)-[:WON_TROPHY   {year:2020, season:'2019-20', manager:'Mikel Arteta'}]->(FACup),
            (Arsenal)-[:WON_TROPHY   {year:2023, season:'2022-23', manager:'Mikel Arteta'}]->(FACup)

            WITH Haaland as a
            MATCH (a)-[:PLAYS_FOR]->(c)<-[:MANAGED]-(m) RETURN a, c, m LIMIT 10;
        """
        graph.flush_database()
        _ = graph.load_scenario_script(script, stats=True)
