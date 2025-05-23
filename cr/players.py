from typing import Optional, List, TYPE_CHECKING


from .miscmodels import Badge, BaseArena, Card, LeagueStatistics, PlayerHouseElement, SupportCard, try_enum, Achievement, Label, Arena, \
    LegendStatistics, \
    SeasonResult
from .enums import (
    Role,
    HERO_ORDER,
    BUILDER_TROOPS_ORDER,
    HOME_TROOP_ORDER,
    SPELL_ORDER,
    SIEGE_MACHINE_ORDER,
    UNRANKED_LEAGUE_DATA,
    ACHIEVEMENT_ORDER,
    SUPER_TROOP_ORDER,
    PETS_ORDER,
    EQUIPMENT,
)
from .abc import BasePlayer
from .player_clan import PlayerClan, PlayerClan as RankedClan
from .utils import cached_property


if TYPE_CHECKING:
    # pylint: disable=cyclic-import
    from .clans import Clan  # noqa


class ClanMember(BasePlayer):
    """Represents a Clash of Clans Clan Member.

    Attributes
    ----------
    tag: :class:`str`
        The player's tag
    name: :class:`str`
        The player's name
    clan: Optional[:class:`Clan`]
        The player's clan. If the player is clanless, this will be ``None``.
    role: :class:`Role`
        The member's role in a clan. To get a string as rendered in-game, do ``str(member.role)``.
    exp_level: :class:`int`
        The member's experience level.
    league: :class:`League`
        The member's current league.
    builder_base_league: :class:`BaseLeague`
        The member's current builder base league.
    trophies: :class:`int`
        The member's trophy count.
    builder_base_trophies: :class:`int`
        The member's builder base trophy count.
    town_hall: :class:`int`
        The player's town hall level. In case the player hasn't logged in since 2019, this will be `0`.
    clan_rank: :class:`int`
        The member's rank in the clan.
    clan_previous_rank: :class:`int`
        The member's rank before the last leaderboard change
        (ie if Bob overtakes Jim in trophies, and they switch ranks on the leaderboard,
        and you want to find out their previous rankings, this will help.).
    builder_base_rank: :class:`int`
        The member's rank in the clan based on builder base trophies.
    donations: :class:`int`
        The member's donation count for this season.
    received: :class:`int`
        The member's donations received count for this season.
    clan_cls: :class:`coc.Clan`
        The class to use to create the :attr:`ClanMember.clan` attribute.
        Ensure any overriding of this inherits from :class:`coc.Clan` or :class:`coc.PlayerClan`.
    league_cls: :class:`coc.League`
        The class to use to create the :attr:`ClanMember.league` attribute.
        Ensure any overriding of this inherits from :class:`coc.League`.
    builder_base_league_cls: :class:`coc.League`
        The class to use to create the :attr:`ClanMember.builder_base_league` attribute.
        Ensure any overriding of this inherits from :class:`coc.BaseLeague`.
    """

    __slots__ = (
        "_client",
        "clan",
        "role",
        "exp_level",
        "arena",
        "trophies",
        "clan_rank",
        "clan_previous_rank",
        "donations",
        "received",
        "clan_cls",
        "arena_cls",
        "lastSeen",
        "clan_chest_points"
    )

    def __init__(self, *, data, client, clan=None, **_):
        super().__init__(data=data, client=client)
        self._client = client
        self.clan_cls = PlayerClan
        self.arena_cls = Arena

        self._from_data(data)
        if clan:
            self.clan = clan

    def _from_data(self, data: dict) -> None:
        data_get = data.get

        self.exp_level: int = data_get("expLevel")
        self.trophies: int = data_get("trophies")

        self.clan_rank: int = data_get("clanRank")
        self.clan_previous_rank: int = data_get("previousClanRank")
        self.donations: int = data_get("donations")
        self.received: int = data_get("donationsReceived")

        self.clan = try_enum(self.clan_cls, data=data_get("clan"), client=self._client)
        self.arena = try_enum(self.arena_cls, data=data_get("arena") or UNRANKED_LEAGUE_DATA, client=self._client)
        self.role = data_get("role") and Role(value=data["role"])
        self.lastSeen = data_get("lastSeen")
        self.clan_chest_points = data_get("clanChestPoints")


    async def get_detailed_clan(self) -> Optional["Clan"]:
        """Get clan details for the player's clan. If the player's clan is ``None``,this will return ``None``.

        Example
        ---------

        .. code-block:: python3

            player = await client.get_player('tag')
            clan = await player.get_detailed_clan()
        """
        return self.clan and await self._client.get_clan(self.clan.tag)


class RankedPlayer(BasePlayer):
    """
    Represents a leaderboard-ranked player.

    Attributes
    ----------
    attack_wins: :class:`int`
        The player's number of attack wins. If retrieving info for builder base leader-boards, this will be ``None``.
    defense_wins: :class:`int`
        The player's number of defense wins. If retrieving info for builder base leader-boards, this will be ``None``.
    builder_base_trophies: :class:`int`
        The player's builder base trophy count. If retrieving info for regular leader-boards, this will be ``None``.
    rank: :class:`int`
        The player's rank in the clan leaderboard.
    previous_rank: :class:`int`
        The member's rank before the last clan leaderboard change
        (ie if Bob overtakes Jim in trophies, and they switch ranks on the leaderboard,
        and you want to find out their previous rankings, this will help.).
    """

    __slots__ = ("clan", "arena", "exp_level", "rank", "previous_rank", "trophies", "clan_cls", "arena_cls",)
    
    def __init__(self, *, data, client, clan=None, **_):
        super().__init__(data=data, client=client)
        self._client = client
        self.clan_cls = RankedClan
        self.arena_cls = Arena
        
        self._from_data(data)
        if clan:
            self.clan = clan

    def _from_data(self, data: dict) -> None:
        data_get = data.get
        self.exp_level: int = data_get("expLevel")
        self.trophies: int = data_get("trophies")
        
        self.rank: int = data_get("rank")
        self.previous_rank: int = data_get("previousRank")
        
        self.clan = try_enum(self.clan_cls, data=data_get("clan"), client=self._client)
        self.arena = try_enum(self.arena_cls, data=data_get("arena") or UNRANKED_LEAGUE_DATA, client=self._client)


class Player(BasePlayer):
    """
    Represents a Clash of Clans Player.

    Attributes
    ----------
    achievement_cls: :class:`Achievement`
        The constructor used to create the :attr:`Player.achievements` list.
        This must inherit from :class:`Achievement`.
    hero_cls: :class:`Hero`
        The constructor used to create the :attr:`Player.heroes` list. This must inherit from :class:`Hero`.
    label_cls: :class:`Label`
        The constructor used to create the :attr:`Player.labels` list. This must inherit from :class:`Label`.
    spell_cls: :class:`Spell`
        The constructor used to create the :attr:`Player.spells` list. This must inherit from :class:`Spell`.
    troop_cls: :class:`Troop`
        The constructor used to create the :attr:`Player.troops` list. This must inherit from :class:`Troop`.
    equipment_cls: :class:`Equipment`
        The constructor used to create the :attr:`Player.equipment` list. This must inherit from :class:`Equipment`.
    attack_wins: :class:`int`
        The number of attacks the player has won this season.
    defense_wins: :class:`int`
        The number of defenses the player has won this season.
    best_trophies: :class:`int`
        The player's best recorded trophies for the home base.
    war_stars: :class:`int`
        The player's total war stars.
    town_hall_weapon: Optional[:class:`int`]
        The player's town hall weapon level, or ``None`` if it doesn't exist.
    builder_hall: :class:`int`
        The player's builder hall level, or 0 if it hasn't been unlocked.
    best_builder_base_trophies: :class:`int`
        The player's best builder base trophy count.
    clan_capital_contributions: :class:`int`
        The player's total contribution to clan capitals
    legend_statistics: Optional[:class:`LegendStatistics`]
        The player's legend statistics, or ``None`` if they have never been in the legend league.
    war_opted_in: Optional[:class:`bool`]
        Whether the player has selected that they are opted "in" (True) for wars, or opted "out" (False).
        This will be ``None`` if the player is not in a clan.
    """
    
    __slots__ = (
        "clan",
        "clan_cls",
        "_support_cards",
        "support_card_cls",
        "current_favorite_card",
        "badges",
        "badge_cls",
        "legacy_best_trophies",
        "current_deck",
        "current_deck_support_cards",
        "arena",
        "arena_cls",
        "role",
        "role_cls",
        "wins",
        "losses",
        "total_donations",
        "league_statistics",
        "league_statistics_cls",
        "_cards",
        "card_cls",
        "exp_level",
        "trophies",
        "best_trophies",
        "donations",
        "donations_received",
        "_achievements",
        "achievement_cls",
        "battle_count",
        "three_crown_wins",
        "challenge_cards_won",
        "challenge_max_wins",
        "tournament_cards_won",
        "tournament_battle_count",
        "war_day_wins",
        "clan_cards_collected",
        "star_points",
        "exp_points",
        "total_exp_points",
        "season_result_cls",
        "current_season_result",
        "last_season_result",
        "best_season_result",
        "progress",
        
        "_iter_achievements",
        "_iter_cards",
        "_iter_support_cards",
    )

    def __init__(self, *, data, client, load_game_data=None, **_):
        self._client = client

        self._achievements = None  # type: Optional[dict]
        self._cards = None  # type: Optional[dict]
        self._support_cards = None  # type: Optional[dict]

        self.achievement_cls = Achievement
        self.card_cls = Card
        self.support_card_cls = SupportCard
        self.arena_cls = Arena
        self.clan_cls = Clan
        self.season_result_cls = SeasonResult
        self.role_cls = Role
        self.league_statistics_cls = LeagueStatistics
        self.badge_cls = Badge

        super().__init__(data=data, client=client)

    def _from_data(self, data: dict) -> None:
        data_get = data.get
        # initialize all attributes
        self.clan: Optional[Clan] = try_enum(self.clan_cls, data=data_get("clan"), client=self._client)
        self._support_cards: List[SupportCard] = [
            try_enum(self.support_card_cls, data=adata, client=self._client) for adata in data_get("supportCards", [])]
        self.current_favorite_card: Optional[Card] = try_enum(self.card_cls, data=data_get("currentFavouriteCard"), client=self._client)
        self.badges: List[Badge] = [try_enum(self.badge_cls, data=adata, client=self._client) for adata in data_get("badges", [])]
        self.legacy_best_trophies: Optional[int] = data_get("legacyTrophyRoadHighScore")
        self.current_deck: List[Card] = [try_enum(self.card_cls, data=adata, client=self._client) for adata in data_get("currentDeck", [])]
        self.current_deck_support_cards: List[SupportCard] = [
            try_enum(self.support_card_cls, data=adata, client=self._client) for adata in data_get("currentDeckSupportCards", [])]
        self.arena: Optional[Arena] = try_enum(self.arena_cls, data=data_get("arena") or UNRANKED_LEAGUE_DATA, client=self._client)
        self.role: Optional[Role] = try_enum(self.role_cls, data=data_get("role"), client=self._client)
        self.wins: Optional[int] = data_get("wins")
        self.losses: Optional[int] = data_get("losses")
        self.total_donations: Optional[int] = data_get("totalDonations")
        self.league_statistics: Optional[LeagueStatistics] = try_enum(self.league_statistics_cls,
                                                                      data=data_get("leagueStatistics"),
                                                                      client=self._client)
        self._cards: List[Card] = [
            try_enum(self.card_cls, data=adata, client=self._client) for adata in data_get("cards", [])]
        self.exp_level: Optional[int] = data_get("expLevel")
        self.trophies: Optional[int] = data_get("trophies")
        self.best_trophies: Optional[int] = data_get("bestTrophies")
        self.donations: Optional[int] = data_get("donations")
        self.donations_received: Optional[int] = data_get("donationsReceived")
        self._achievements: List[Achievement] = [
            try_enum(self.achievement_cls, data=adata, client=self._client) for adata in data_get("achievements", [])
        ]
        self.battle_count: Optional[int] = data_get("battleCount")
        self.three_crown_wins: Optional[int] = data_get("threeCrownWins")
        self.challenge_cards_won: Optional[int] = data_get("challengeCardsWon")
        self.challenge_max_wins: Optional[int] = data_get("challengeMaxWins")
        self.tournament_cards_won: Optional[int] = data_get("tournamentCardsWon")
        self.tournament_battle_count: Optional[int] = data_get("tournamentBattleCount")
        self.war_day_wins: Optional[int] = data_get("warDayWins")
        self.clan_cards_collected: Optional[int] = data_get("clanCardsCollected")
        self.star_points: Optional[int] = data_get("starPoints")
        self.exp_points: Optional[int] = data_get("expPoints")
        self.total_exp_points: Optional[int] = data_get("totalExpPoints")
        self.current_season_result: Optional[SeasonResult] = try_enum(self.season_result_cls,
                                                                      data=data_get('currentPathOfLegendSeasonResult'),
                                                                      client=self._client)
        self.last_season_result: Optional[SeasonResult] = try_enum(self.season_result_cls,
                                                                   data=data_get('previousPathOfLegendSeasonResult'),
                                                                   client=self._client)
        self.best_season_result: Optional[SeasonResult] = try_enum(self.season_result_cls,
                                                                   data=data_get('bestPathOfLegendSeasonResult'),
                                                                   client=self._client)
        self.progress = data_get("progress")
        


    

    def _inject_clan_member(self, member):
        if member:
            self.clan_rank = getattr(member, "clan_rank", None)
            self.clan_previous_rank = getattr(member, "clan_previous_rank", None)



    @cached_property("_cs_labels")
    def labels(self) -> List[Label]:
        """List[:class:`Label`]: A :class:`List` of :class:`Label`\s that the player has."""
        return list(self._iter_labels)

    @cached_property("_cs_achievements")
    def achievements(self) -> List[Achievement]:
        """List[:class:`Achievement`]: A list of the player's achievements."""
        # at the time of writing, the API presents achievements in the order
        # added to the game which doesn't match in-game order.
        achievement_dict = {a.name: a for a in self._iter_achievements}
        sorted_achievements = {}
        for name in ACHIEVEMENT_ORDER:
            try:
                sorted_achievements[name] = achievement_dict[name]
            except KeyError:
                continue

        self._achievements = sorted_achievements
        return list(sorted_achievements.values())

    def get_achievement(self, name: str, default_value=None) -> Optional[Achievement]:
        """Gets an achievement with the given name.

        Parameters
        -----------
        name: :class:`str`
            The name of an achievement as found in-game.
        default_value
            The value to return if the ``name`` is not found. Defaults to ``None``.

        Returns
        --------
        Optional[:class:`Achievement`]
            The returned achievement or the ``default_value`` if not found, which defaults to ``None``.
        """
        if not self._achievements:
            _ = self.achievements

        try:
            return self._achievements[name]
        except KeyError:
            return default_value
