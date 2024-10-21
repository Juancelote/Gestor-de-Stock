from fastapi import APIRouter, HTTPException
from DB.models.items_model import ItemModel
from DB.schemas.item import item_schema, items_schema
from DB.client import db_client
from bson import ObjectId

item_route = APIRouter(prefix="/Item", tags=["Item"])

# verificamos si existe algun item con el campo "name", devuelve un boolean True/False, en caso de encontrarlo, lo retorna.
def item_exists(name: str) -> bool:
    existing_item = db_client.local.item.find_one({"name": name})
    return existing_item is not None

# creamos un nuevo item.
@item_route.post("/Create", response_model=ItemModel)
async def create_item(item: ItemModel):

    # Verificar si el ítem ya existe al momento de la inserción de los datos.
    if item_exists(item.name):
        raise HTTPException(status_code=400, detail="El ítem ya existe en la base de datos")

    # en caso de que no lo encuentre, continuamos con la inserción.
    item_dic = dict(item)
    del item_dic["id"]  # Eliminamos el campo "id" para evitar conflictos con el _id autogenerado por MongoDB.

    try:
        # Insertar el nuevo ítem.
        id = db_client.local.item.insert_one(item_dic).inserted_id
        new_item = item_schema(db_client.local.item.find_one({"_id": id}))
        return new_item
    
    # ante cualquier error, se captura en el bloque except y lo gestionamos notificando del error.
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al insertar el ítem: {e}")


# tomamos todos los items que se encuentren en la DB y los transformamos a una lista. Por cada item, una lista con sus keys/values.
@item_route.get("/GetAll", response_model=list[ItemModel])
async def get_all_items():

    # en este bloque del try.
    try:
        # lo que obtengamos de el motodo .find() que realizamos en la base de datos mediante su conexion, lo pasamos al esquema de items que tenemos.
        items = items_schema(db_client.local.item.find())
        return items
    
    # en este bloque del except, capturamos todos los errores y los mostramos.
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los ítems: {e}")


# tomamos solo un item, en este caso, el identificador unico sera el nombre.
@item_route.get("/GetByName/{name}", response_model=ItemModel)
async def get_item_by_name(name: str):

    # en este bloque del try.
    try:
        # realizamos una busqueda con el metodo .find_one() y si no lo encuentra, gestionar el error del not found.
        item = db_client.local.item.find_one({"name": name})
        if not item:
            raise HTTPException(status_code=404, detail="Ítem no encontrado")
        
        # de encontrarlo, solo lo devolveremos.
        return item_schema(item)
    
    # en este bloque del except, capturamos todos los errores y los mostramos.
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener el ítem: {e}")


# Tomamos un item para actualizar, especificando el id a modificar.   
@item_route.put("/Update/{id}", response_model=ItemModel)
async def update_item(id: str, item: ItemModel):
    # transformamos el modelo de item a un diccionario.
    user_dic = dict(item)
    # Eliminamos la key id, ya que mongo tiene un autogenerado de id.
    del user_dic["id"]

    # En este bloque se intenta:
    try:
        """ 
        Se intenta actualizar un item con el metodo .update_one()
        Empleamos un ObjectId, ya que se debe de convertir el id de cadena a un objeto antes de realizar alguna consulta con el id
        El $set se asegura de que solo los campos proporcionados por el user_dic sean actualizados.
        """
        update = db_client.local.item.update_one({"_id": ObjectId(id)})
        
        # Si no se encuentra el item, osea el contador de match es igual a 0, se gestiona el error.
        if update.matched_count == 0:
            raise HTTPException(status_code=404, detail="Ítem no encontrado para actualizar")
        
        # De haber encontrado una coincidencia, entonces procede a actualizarlo.
        updated_item = db_client.local.item.find_one({"_id": ObjectId(id)})

        # Y lo devolvemos con el esquema que pretende recibir FastAPI.
        return item_schema(updated_item)
    
    # Cualquier error que surja, sera capturado en el except y gestionado, mostrando el error en cuestion.
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar el ítem: {e}")


# Tomamos un item para su eliminacion, mediante el id.
@item_route.delete("/Delete/{id}", response_model=ItemModel)
async def delete_item(id: str):

    # Se intenta:
    try:
        """ 
        Encontrar un item con el metodo .find_one()
        Como en el endpoint anterior, utilizamos la conversion del id, de cadena a objeto, para asi poder usarlo en nuestro esquema de fastAPI.
        """
        item = db_client.local.item.find_one({"_id": ObjectId(id)})
        
        # Si no se encuentra el item, se gestiona el error.
        if not item:
            raise HTTPException(status_code=404, detail="Ítem no encontrado para eliminar")
        
        # De haber encontrado el item, procede a eliminarlo con el metodo.delete_one().
        db_client.local.item.delete_one({"_id": ObjectId(id)})
        
        # Devuelve el item que elimino.
        return item_schema(item)
    
    # Cualquier error que surja, sera capturado en el except y gestionado, mostrando el error en cuestion.
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar el ítem: {e}")