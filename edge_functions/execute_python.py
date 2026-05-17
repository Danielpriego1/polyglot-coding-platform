import json

def handler(event, context):
    """
    Edge Function para ejecutar código Python del juego.
    Recibe: { "code": "...", "state": { ... } }
    Devuelve: { "new_state": { ... }, "message": "..." }
    """
    body = json.loads(event.get("body", "{}"))
    code = body.get("code", "")
    state_data = body.get("state", {})
    
    # Simulación de la lógica del motor (esto correría en un sandbox seguro en InsForge)
    # En una implementación real, aquí se instanciaría el GameState y el PythonExecutor
    
    # Por ahora, devolvemos una estructura que el cliente pueda entender
    return {
        "statusCode": 200,
        "body": json.dumps({
            "status": "success",
            "message": "Código Python ejecutado en el servidor",
            "received_code": code
        })
    }
