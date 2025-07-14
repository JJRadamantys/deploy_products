import streamlit as st
import pandas as pd
from google.cloud import firestore
from google.oauth2 import service_account

import json
key_dic = json.loads(st.secrets["textkey"])

creds = service_account.Credentials.from_service_account_info(key_dic)
#db = firestore.Client(credentials=creds, project="names-project-demo.json")
db = firestore.Client(credentials=creds, project="products-project-213c1")
dbProducto = db.collection("producto")


##############################################

st.header("Nuevo registro")

# Campos
codigo = st.text_input("Código")
nombre = st.text_input("Nombre")
precio = st.text_input("Precio")
existencias = st.text_input("Existencias")
stock_minimo = st.text_input("Stock_mínimo")
stock_maximo = st.text_input("Stock_máximo")


submit = st.button("Crear nuevo registro")

# Once the name has submitted, upload in to the database

if codigo and nombre and precio and existencias and stock_minimo and stock_maximo and submit:
  doc_ref = db.collection("producto").document(codigo)
  doc_ref.set({
      "codigo": codigo,
      "nombre": nombre,
      "precio": precio,
      "existencias": existencias,
      "stock_minimo": stock_minimo,
      "stock_maximo": stock_maximo
  })
  st.sidebar.write("Registro insertado correctamente")

#Muestrar el dataframe de los productos
product_ref = list(db.collection(u'producto').stream())
product_dict = list(map(lambda x: x.to_dict(), product_ref))
product_dataframe = pd.DataFrame(product_dict)
st.dataframe(product_dataframe)


######################################################

def loadBycodigo(codigo):
  codigo_ref = dbProducto.where(u'codigo', u'==', codigo)
  currentCodigo = None
  for mycodigo in codigo_ref.stream():
    currentCodigo = mycodigo
  return currentCodigo

st.sidebar.markdown("""---""")
st.sidebar.subheader("Buscar codigo")
codigoSearch = st.sidebar.text_input("codigo")
btnFiltrar = st.sidebar.button("Buscar")

if(btnFiltrar):
  doc = loadBycodigo(codigoSearch)
  if(doc is None):
    st.sidebar.write("Codigo no existe")
  else:
    st.sidebar.write(doc.to_dict())


######################################################
st.sidebar.markdown("""---""")
btnEliminar = st.sidebar.button("Eliminar Producto")
if(btnEliminar):
  deleteproducto = loadBycodigo(codigoSearch)
  if(deleteproducto is None):
    st.sidebar.write(f"{codigoSearch} no existe")
  else:
    dbProducto.document(deleteproducto.id).delete()
    st.sidebar.write(f"{codigoSearch} ha sido eliminado")

#########################################################
st.sidebar.markdown("""---""")
st.sidebar.subheader("Actualizar producto")

# Entrada para el nuevo precio y otros campos
newprecio = st.sidebar.text_input("Nuevo precio")
newexistencias = st.sidebar.text_input("Nuevas existencias")
newstock_minimo = st.sidebar.text_input("Nuevo stock mínimo")
newstock_maximo = st.sidebar.text_input("Nuevo stock máximo")

btnActualizarprecio = st.sidebar.button("Actualizar")

if btnActualizarprecio:
    producto_doc = loadBycodigo(codigoSearch)

    if producto_doc is None:
        st.sidebar.warning(f"⚠️ El producto con código {codigoSearch} no existe.")
    else:
        try:
            # Obtener referencia directa al documento por su ID (que es el código)
            doc_ref = dbProducto.document(codigoSearch)

            # Realizar la actualización solo con campos ingresados
            update_fields = {}
            if newprecio: update_fields["precio"] = newprecio
            if newexistencias: update_fields["existencias"] = newexistencias
            if newstock_minimo: update_fields["stock_minimo"] = newstock_minimo
            if newstock_maximo: update_fields["stock_maximo"] = newstock_maximo

            # Si hay campos que actualizar, procede
            if update_fields:
                doc_ref.update(update_fields)
                st.sidebar.success(f"✅ {codigoSearch} ha sido actualizado.")
            else:
                st.sidebar.info("ℹ️ No se ingresaron campos para actualizar.")

        except Exception as e:
            st.sidebar.error(f"❌ Error al actualizar: {e}")
