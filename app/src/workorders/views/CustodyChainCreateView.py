# En tu vista de creación, después de crear la cadena de custodia,
# en lugar de retornar solo el ID y consecutivo, retorna el objeto completo:

return Response(
    {
        "success": True,
        "message": "Cadena de custodia creada exitosamente",
        "data": {
            "custody_chain": CustodyChainSerializer(custody_chain).data,
        },
    },
    status=status.HTTP_201_CREATED,
)
