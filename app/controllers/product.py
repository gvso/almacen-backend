from app.db import db
from app.models import (
    Product,
    ProductTranslation,
    ProductVariation,
    ProductVariationTranslation,
)
from app.repos import ProductRepo


class ProductController:
    def __init__(self, product_repo: ProductRepo) -> None:
        self._product_repo = product_repo

    def clone_product(self, product_id: int) -> Product | None:
        """Clone a product with all its translations, variations, and tag associations.

        Returns the cloned product or None if the original product was not found.
        """
        product = self._product_repo.get(product_id)
        if not product:
            return None

        # Create cloned product with "(Copy)" appended to name
        cloned_product = Product(
            name=f"{product.name} (Copy)",
            description=product.description,
            price=product.price,
            image_url=product.image_url,
            order=product.order,
            is_active=False,  # Start as inactive so admin can review before publishing
            type=product.type,
        )
        db.session.add(cloned_product)
        db.session.flush()  # Get the ID for the cloned product

        # Clone translations
        for translation in product.translations:
            cloned_translation = ProductTranslation(
                product_id=cloned_product.id,
                language=translation.language,
                name=f"{translation.name} (Copy)",
                description=translation.description,
            )
            db.session.add(cloned_translation)

        # Clone variations with their translations
        for variation in product.variations:
            cloned_variation = ProductVariation(
                product_id=cloned_product.id,
                name=variation.name,
                price=variation.price,
                image_url=variation.image_url,
                order=variation.order,
                is_active=variation.is_active,
            )
            db.session.add(cloned_variation)
            db.session.flush()  # Get the ID for the cloned variation

            # Clone variation translations
            for var_translation in variation.translations:
                cloned_var_translation = ProductVariationTranslation(
                    variation_id=cloned_variation.id,
                    language=var_translation.language,
                    name=var_translation.name,
                )
                db.session.add(cloned_var_translation)

        # Clone tag associations
        for tag in product.tags:
            cloned_product.tags.append(tag)

        db.session.commit()
        db.session.refresh(cloned_product)
        return cloned_product
