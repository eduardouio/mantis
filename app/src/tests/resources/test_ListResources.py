from django.urls import reverse_lazy
from tests.BaseTestView import BaseTestView
from equipment.views import (
    ResourceItemList,
    ResourceItemDetail,
    CreateResourceItem,
    UpdateResourceItem,
    RemoveResourceItem,
    ListVehicle,
    DetailVehicle,
    CreateVehicle,
    UpdateVehicle,
    DeleteVehicle
    )


class TestResourceItem(BaseTestView):

    def test_ListView(self, client_logged):
        url = reverse_lazy('resource_list')
        self.test_client_logged(client_logged, url)