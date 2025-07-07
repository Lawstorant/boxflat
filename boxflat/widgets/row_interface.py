from abc import ABC, abstractmethod

class BoxflatRowInterface(ABC):

    @abstractmethod
    def create_purchase_invoice(self, purchase):
        pass

    @abstractmethod
    def create_sale_invoice(self, sale):
        log.debug('Creating sale invoice', sale)
