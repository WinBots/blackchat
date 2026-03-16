"""
Cache module – Redis com fallback seguro.
Se o Redis não estiver disponível, o sistema continua funcionando
indo direto ao banco de dados (apenas mais lento).
"""
