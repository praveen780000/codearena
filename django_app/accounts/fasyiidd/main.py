from fastapi import FastAPI
from models import product      


app = FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome to the FastAPI application!"}

products=[
product(id=1, name="Sample Product", price=19.99, description="This is a sample product."),
product(id=2, name="Another Product", price=29.99, description="This is another product."),
product(id=3, name="Third Product", price=39.99, description="This is the third product.")]


@app.get("/products")
def get_products():
    return products

@app.get("/product/{id}")
def get_product(id: int):
    for product in products:
        if product.id == id:
            return product
    return {"error": "Product not found"}

@app.post("/product")
def create_product(product: product):
    products.append(product)
    return product


@app.put("/product")
def update_product(id: int, product:product):
    for i in range(len(products)):
        if products[i].id == id:
            products[i] = product
            return product
    return {"error": "Product not found"}


@app.delete("/product")
def delete_product(id:int):
    for i in range(len(products)):
        if products[i].id == id:
            del products[i]
            return {"message": "Product deleted successfully"}
    return {"error": "Product not found"}