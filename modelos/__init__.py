from .cliente import Cliente, ClienteBase
from .ofertador import Ofertador, OfertadorBase
from .veiculo import Veiculo, VeiculoBase
from .documento import Documento, DocumentoBase
from .aluguel import Aluguel, AluguelBase
from .pagamento import Pagamento, PagamentoBase

__all__ = ["Cliente", "Ofertador", "Veiculo", "Documento", "Aluguel", "Pagamento"]