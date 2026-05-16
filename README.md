# API-AluguelVeiculo

### Diagrama Entidade-Relacionamento (Aluguel de Veículos)

```mermaid
erDiagram
    %% Relacionamentos
    OFERTADOR ||--o{ ALUGUEL : "disponibiliza"
    CLIENTE ||--o{ ALUGUEL : "realiza"
    VEICULO ||--o{ ALUGUEL : "reservado_em"
    ALUGUEL ||--|| PAGAMENTO : "possui"
    VEICULO ||--o{ DOCUMENT : "tem_anexos"

    %% Entidades
    OFERTADOR {
        int id PK
        string nome
        string CNPJ
        string endereco
    }

    CLIENTE {
        int id PK
        string nome
        string CPF
        string telefone
    }

    VEICULO {
        int id PK
        string placa
        string tipo
        string modelo
        string status
    }

    ALUGUEL {
        int id PK
        int fk_cliente FK
        int fk_veiculo FK
        int fk_ofertador FK
        date data_inicio
        date data_fim
        string status
    }

    PAGAMENTO {
        int id PK
        int fk_aluguel FK
        float valor_total
        string metodo
        date data_pagamento
    }

    DOCUMENT {
        int id PK
        string original_filename
        string content_type
        string extension
        int size_bytes
        datetime created_at
        int fk_veiculo FK
    }