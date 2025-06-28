from datetime import timedelta
from django.utils import timezone
from accounts.utils import log_activity
from products.models import Product, PlantedProduct
from products.serializers import ProductSerializer, PlantedProductSerializer, PlantedProductSerializerListAndRetrieve
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from accounts.permissions import IsAdminUser
from products.pagination import ProductPageNumberPagination
from rest_framework.views import APIView
from django.db.models import Sum, F, Max
from decimal import Decimal
from collections import defaultdict
from regions.models import Region


class ProductModelViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    pagination_class = ProductPageNumberPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        elif self.action in ['create', 'update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]


class PlantedProductModelViewSet(ModelViewSet):
    serializer_class = PlantedProductSerializer
    queryset = PlantedProduct.objects.all()

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ['retrieve', 'list']:
            return queryset.filter(owner=self.request.user.pk)
        return queryset

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return PlantedProductSerializerListAndRetrieve
        return self.serializer_class

    def perform_create(self, serializer):
        instance = serializer.save(owner=self.request.user)
        log_activity(instance.owner, "CREATE", instance)

    def perform_update(self, serializer):
        instance = serializer.save()
        log_activity(instance.owner, "UPDATE", instance)

    def perform_destroy(self, instance):
        log_activity(instance.owner, "DELETE", instance)
        instance.delete()


class WPHPerRegion(APIView):
    """Calculate Weight Per Hectare for a specific region or all regions"""
    permission_classes = [AllowAny]

    def get(self, request):
        region_id = request.query_params.get("region_id")

        # Filter by region if provided
        queryset = PlantedProduct.objects.all()
        if region_id:
            try:
                region = Region.objects.get(pk=region_id)
                queryset = queryset.filter(region=region)
                region_name = region.name
            except Region.DoesNotExist:
                return Response(
                    {"error": "Region not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            region_name = "All Regions"

        # Calculate aggregated values
        aggregated = queryset.aggregate(
            total_expecting_weight=Sum('expecting_weight'),
            total_planting_area=Sum('planting_area')
        )

        total_weight = aggregated['total_expecting_weight'] or Decimal('0')
        total_area = aggregated['total_planting_area'] or Decimal('0')

        # Calculate WPH (avoid division by zero)
        wph = float(total_weight / total_area) if total_area > 0 else 0.0

        data = {
            "region": region_name,
            "expecting_weight": float(total_weight),
            "planting_area": float(total_area),
            "wph": wph,
            "total_records": queryset.count()
        }

        return Response(data, status=status.HTTP_200_OK)


class WPHPerRegionPerProduct(APIView):
    """Calculate Weight Per Hectare grouped by product for a specific region"""
    permission_classes = [AllowAny]

    def get(self, request):
        region_id = request.query_params.get("region_id")
        product_id = request.query_params.get("product_id")

        # Start with all planted products
        queryset = PlantedProduct.objects.select_related('product', 'region')

        # Filter by region if provided
        if region_id:
            try:
                region = Region.objects.get(pk=region_id)
                queryset = queryset.filter(region=region)
                region_name = region.name
            except Region.DoesNotExist:
                return Response(
                    {"error": "Region not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            region_name = "All Regions"

        # Filter by product if provided
        if product_id:
            try:
                product = Product.objects.get(pk=product_id)
                queryset = queryset.filter(product=product)
            except Product.DoesNotExist:
                return Response(
                    {"error": "Product not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

        # Group by product and calculate WPH for each
        product_data = defaultdict(lambda: {
            'expecting_weight': Decimal('0'),
            'planting_area': Decimal('0'),
            'count': 0
        })

        for planted_product in queryset:
            product_name = planted_product.product.name if planted_product.product else "Unknown Product"
            product_data[product_name]['expecting_weight'] += planted_product.expecting_weight
            product_data[product_name]['planting_area'] += planted_product.planting_area
            product_data[product_name]['count'] += 1

        # Calculate WPH for each product
        result = []
        for product_name, data in product_data.items():
            wph = float(data['expecting_weight'] / data['planting_area']) if data['planting_area'] > 0 else 0.0
            result.append({
                "product_name": product_name,
                "expecting_weight": float(data['expecting_weight']),
                "planting_area": float(data['planting_area']),
                "wph": wph,
                "planted_records": data['count']
            })

        # Sort by WPH descending
        result.sort(key=lambda x: x['wph'], reverse=True)

        response_data = {
            "region": region_name,
            "products": result,
            "total_products": len(result)
        }

        return Response(response_data, status=status.HTTP_200_OK)


class WPHComparison(APIView):
    """Compare WPH across different regions for all products or specific product"""
    permission_classes = [AllowAny]

    def get(self, request):
        product_id = request.query_params.get("product_id")

        queryset = PlantedProduct.objects.select_related('product', 'region')

        # Filter by product if provided
        if product_id:
            try:
                product = Product.objects.get(pk=product_id)
                queryset = queryset.filter(product=product)
                product_name = product.name
            except Product.DoesNotExist:
                return Response(
                    {"error": "Product not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            product_name = "All Products"

        # Group by region
        region_data = defaultdict(lambda: {
            'expecting_weight': Decimal('0'),
            'planting_area': Decimal('0'),
            'count': 0
        })

        for planted_product in queryset:
            region_name = planted_product.region.name if planted_product.region else "Unknown Region"
            region_data[region_name]['expecting_weight'] += planted_product.expecting_weight
            region_data[region_name]['planting_area'] += planted_product.planting_area
            region_data[region_name]['count'] += 1

        # Calculate WPH for each region
        result = []
        for region_name, data in region_data.items():
            wph = float(data['expecting_weight'] / data['planting_area']) if data['planting_area'] > 0 else 0.0
            result.append({
                "region_name": region_name,
                "expecting_weight": float(data['expecting_weight']),
                "planting_area": float(data['planting_area']),
                "wph": wph,
                "planted_records": data['count']
            })

        # Sort by WPH descending
        result.sort(key=lambda x: x['wph'], reverse=True)

        response_data = {
            "product": product_name,
            "regions": result,
            "total_regions": len(result)
        }

        return Response(response_data, status=status.HTTP_200_OK)


class WPHMatrix(APIView):
    """Get a matrix of WPH values: regions vs products"""
    permission_classes = [AllowAny]

    def get(self, request):
        queryset = PlantedProduct.objects.select_related('product', 'region')

        # Group by region and product
        matrix_data = defaultdict(lambda: defaultdict(lambda: {
            'expecting_weight': Decimal('0'),
            'planting_area': Decimal('0'),
            'count': 0
        }))

        for planted_product in queryset:
            region_name = planted_product.region.name if planted_product.region else "Unknown Region"
            product_name = planted_product.product.name if planted_product.product else "Unknown Product"

            matrix_data[region_name][product_name]['expecting_weight'] += planted_product.expecting_weight
            matrix_data[region_name][product_name]['planting_area'] += planted_product.planting_area
            matrix_data[region_name][product_name]['count'] += 1

        # Build the response matrix
        result = []
        for region_name, products in matrix_data.items():
            region_row = {
                "region_name": region_name,
                "products": []
            }

            for product_name, data in products.items():
                wph = float(data['expecting_weight'] / data['planting_area']) if data['planting_area'] > 0 else 0.0
                region_row["products"].append({
                    "product_name": product_name,
                    "expecting_weight": float(data['expecting_weight']),
                    "planting_area": float(data['planting_area']),
                    "wph": wph,
                    "planted_records": data['count']
                })

            # Sort products by WPH descending
            region_row["products"].sort(key=lambda x: x['wph'], reverse=True)
            result.append(region_row)

        # Sort regions by best WPH (average of all products)
        for region in result:
            if region["products"]:
                region["avg_wph"] = sum(p["wph"] for p in region["products"]) / len(region["products"])
            else:
                region["avg_wph"] = 0.0

        result.sort(key=lambda x: x['avg_wph'], reverse=True)

        return Response({"matrix": result}, status=status.HTTP_200_OK)


class TotalProductionThisMonth(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        planted_products = PlantedProduct.objects.filter(created_at__gt=timezone.now() - timedelta(days=30))
        total_weight = planted_products.aggregate(total_weight=Sum('planting_area'))['total_weight']
        return Response({"total_weight": total_weight}, status=status.HTTP_200_OK)


class HighestWPH(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        planted_products = PlantedProduct.objects.values('expecting_weight', 'planting_area')
        wph = planted_products.annotate(wph=F("expecting_weight") / F("planting_area"))
        max_whp = wph.order_by('-wph')[0]['wph']
        return Response({"whp": max_whp}, status=status.HTTP_200_OK)


class TopPerformingRegion(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        top_region = PlantedProduct.objects.values('region__name').annotate(
            total_production=Sum('expecting_weight')
        ).order_by('-total_production').first()

        if top_region:
            return Response({
                "region": top_region['region__name'],
                "total_production": top_region['total_production']
            })
        else:
            return Response({
                "region": "No data",
                "total_production": 0
            })
