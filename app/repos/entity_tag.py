from app.models.tag import EntityTag, EntityType
from app.repos.base import Repo


class EntityTagRepo(Repo[EntityTag]):
    def __init__(self) -> None:
        super().__init__(EntityTag)

    def find(self, entity_type: EntityType, entity_id: int, tag_id: int) -> EntityTag | None:
        """Find an entity tag by entity type, entity id, and tag id."""
        return (
            self.get_query()
            .filter(
                EntityTag.entity_type == entity_type,
                EntityTag.entity_id == entity_id,
                EntityTag.tag_id == tag_id,
            )
            .first()
        )

    def exists(self, entity_type: EntityType, entity_id: int, tag_id: int) -> bool:
        """Check if an entity tag exists."""
        return self.find(entity_type, entity_id, tag_id) is not None

    def add_tag(self, entity_type: EntityType, entity_id: int, tag_id: int) -> EntityTag:
        """Add a tag to an entity."""
        entity_tag = EntityTag(
            entity_type=entity_type,
            entity_id=entity_id,
            tag_id=tag_id,
        )
        return self.persist(entity_tag)

    def remove_tag(self, entity_type: EntityType, entity_id: int, tag_id: int) -> bool:
        """Remove a tag from an entity. Returns True if deleted, False if not found."""
        deleted = (
            self.get_query()
            .filter(
                EntityTag.entity_type == entity_type,
                EntityTag.entity_id == entity_id,
                EntityTag.tag_id == tag_id,
            )
            .delete()
        )
        self.commit()
        return deleted > 0
