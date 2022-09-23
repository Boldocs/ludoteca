from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, ExpressionWrapper, F, Sum, fields
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView
from django_filters import rest_framework as django_filters
from rest_framework import filters, viewsets, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt import authentication

from backend.api import utils
from backend.api.filters import LibraryGameFilter, StoreGameFilter
from backend.api.models import Supplier, LibraryGame, StoreGame, Withdraw, Location
from backend.api.serializers.legacy import SupplierSerializer, LibraryGameSerializer, StoreGameSerializer, \
    AnonStoreGameSerializer, WithdrawSerializer, LocationSerializer
from backend.api.serializers.users import PlayerSerializer, UserSerializer

User = get_user_model()

# Serve Vue Application
index_view = never_cache(TemplateView.as_view(template_name="index.html"))


class StandardResultsSetPagination(PageNumberPagination):
    """30 is divisible by 2,3,4,5 and 6 making it flexible to adjust frontend layout.
    All requests with pagination should take page_size with a base of 60"""

    page_size = 30
    page_size_query_param = "page_size"
    max_page_size = 1000


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.order_by("name")
    serializer_class = SupplierSerializer
    authentication_classes = (authentication.JWTAuthentication,)
    permission_classes = (permissions.IsAdminUser,)
    filter_backends = (filters.SearchFilter, django_filters.DjangoFilterBackend)
    search_fields = ["name"]


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = User.objects.order_by("first_name", "last_name")
    serializer_class = PlayerSerializer
    authentication_classes = (authentication.JWTAuthentication,)
    filter_backends = (filters.SearchFilter, django_filters.DjangoFilterBackend)
    search_fields = ["first_name", "last_name", "username", "email"]
    # permission_classes = (permissions.IsAdminUser,)


class LibraryGameViewSet(viewsets.ModelViewSet):
    queryset = LibraryGame.objects.all().annotate(num_withdraws=Count("withdraw"))
    serializer_class = LibraryGameSerializer
    search_fields = ["game__name", "game__other_names"]
    filter_backends = (
        filters.SearchFilter,
        django_filters.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    filterset_class = LibraryGameFilter
    ordering_fields = ["game__name", "game__year", "game__rank", "num_withdraws"]
    ordering = "game__name"
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    authentication_classes = [authentication.JWTAuthentication]
    pagination_class = StandardResultsSetPagination

    def perform_create(self, serializer):
        bggid = serializer.initial_data["game_id"]
        game = utils.BGGGame.find(bggid)

        if game is None:
            game = utils.BGGGame.create(bggid)

        serializer.is_valid()
        serializer.save(game=game)


class StoreGameViewSet(viewsets.ModelViewSet):
    queryset = StoreGame.objects.all()
    search_fields = ["game__name", "game__other_names"]
    filter_backends = (
        filters.SearchFilter,
        django_filters.DjangoFilterBackend,
        filters.OrderingFilter,
    )


    ordering_fields = ["game__name", "game__year", "game__rank", "selling_price"]
    ordering = "game__name"
    filterset_class = StoreGameFilter
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    authentication_classes = [authentication.JWTAuthentication]
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return StoreGameSerializer
        return AnonStoreGameSerializer

    def perform_create(self, serializer):
        bggid = serializer.initial_data["game_id"]
        game = utils.BGGGame.find(bggid)

        if game is None:
            game = utils.BGGGame.create(bggid)

        serializer.is_valid()
        serializer.save(game=game)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("first_name", "last_name")
    serializer_class = UserSerializer
    authentication_classes = [authentication.JWTAuthentication]
    permission_classes = [
        permissions.IsAdminUser |
        permissions.DjangoObjectPermissions |
        permissions.DjangoModelPermissions
    ]

    def get_object(self):
        pk = self.kwargs.get("pk")

        if pk == "current":
            return self.request.user

        return super().get_object()


class WithdrawViewSet(viewsets.ModelViewSet):
    queryset = Withdraw.objects.all()
    serializer_class = WithdrawSerializer
    authentication_classes = [authentication.JWTAuthentication]
    permission_classes = (permissions.IsAdminUser,)


class StatisticsViewSet(APIView):
    def get(self, request):
        return Response(
            {
                "library": self._load_library_statistics(),
                "store": self._load_store_statistics(),
            }
        )

    def _load_library_statistics(self):
        # Load users ordered by number of withdraws
        users = [
            {
                "id": user.id,
                "name": f"{user.first_name} {user.last_name}",
                "count": user.num_withdraws,
            }
            for user in User.objects.annotate(num_withdraws=Count("withdraw")).order_by(
                "-num_withdraws"
            )
        ][:5]

        # Load games order by number of withdraws
        all_popular_games = LibraryGame.objects.annotate(
            num_withdraws=Count("withdraw")
        ).order_by("-num_withdraws")

        ongoing_withdraws = Withdraw.objects.filter(
            date_returned__isnull=True
        ).aggregate(
            min_players=Sum("game__game__min_players"),
            max_players=Sum("game__game__max_players"),
            total=Count("*"),
        )

        duration = ExpressionWrapper(
            F("date_returned") - F("date_withdrawn"),
            output_field=fields.DurationField(),
        )
        average_duration = (
            Withdraw.objects.annotate(duration=duration)
            .filter(date_returned__isnull=False)
            .aggregate(average=Avg(duration))
        )

        popular_games = [
            {
                "id": game.id,
                "bggid": game.game.bggid,
                "game": f"{game.game.name}",
                "requisitions": game.num_withdraws,
            }
            for game in all_popular_games[:5]
        ]

        return {
            "games": {
                "total": LibraryGame.objects.all().count(),
                "being_played": ongoing_withdraws.get("total"),
                "not_checked_in": LibraryGame.objects.filter(
                    location__isnull=True
                ).count(),
            },
            "requisitors": {
                "total": User.objects.all().count(),
            },
            "withdraws": {
                "total": Withdraw.objects.all().count(),
                "recent": {
                    "out": [
                        {
                            "game_id": w.game_id,
                            "bggid": w.game.game.bggid,
                            "game": w.game.game.name,
                            "image": w.game.game.image,
                            "date": w.date_withdrawn,
                        }
                        for w in Withdraw.objects.all().order_by("-date_withdrawn")[:8]
                    ],
                    "in": [
                        {
                            "game_id": w.game_id,
                            "bggid": w.game.game.bggid,
                            "image": w.game.game.image,
                            "game": w.game.game.name,
                            "date": w.date_returned,
                        }
                        for w in Withdraw.objects.all().order_by("-date_returned")[:8]
                    ],
                },
                "popular": {"requisitors": users, "games": popular_games},
                "players": {
                    "min_players": ongoing_withdraws.get("min_players"),
                    "max_players": ongoing_withdraws.get("max_players"),
                },
                "duration": average_duration,
            },
        }

    def _load_store_statistics(self):
        return {
            "total": StoreGame.objects.all().count(),
            "available": StoreGame.objects.filter(stock__gte=0).count(),
        }


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.order_by("name").all()
    serializer_class = LocationSerializer
