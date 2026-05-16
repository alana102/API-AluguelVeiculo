# API-AluguelVeiculo

### Diagrama Entidade-Relacionamento (Aluguel de Veículos)

```mermaid
erDiagram
    %% Relacionamentos
    CLIENTE }|--|{ VEICULO : "aluga"
    OFERTADOR ||--o{ VEICULO : "cadastra"
    CLIENTE ||--o{ ALUGUEL : "solicita"
    VEICULO ||--o{ ALUGUEL : "vincula"
    ALUGUEL ||--|| PAGAMENTO : "gera"
    VEICULO ||--o{ DOCUMENTO : "anexa"

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
        int fk_ofertador FK
        string placa
        string tipo
        string modelo
        string status
    }

    ALUGUEL {
        int id PK
        int fk_cliente FK
        int fk_veiculo FK
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

    DOCUMENTO {
        int id PK
        int fk_veiculo FK
        string original_filename
        string content_type
        string extension
        int size_bytes
        datetime created_at
        int fk_veiculo FK
    }