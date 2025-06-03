#!/usr/bin/env python3

import sys
import os
import pytest
import json
import importlib.util
from pathlib import Path
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).parent.parent))

spec = importlib.util.spec_from_file_location(
    "generate_notes", 
    Path(__file__).parent.parent / "scripts" / "02_generate_notes.py"
)
generate_notes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generate_notes)

Note = generate_notes.Note
StudyNotesResponse = generate_notes.StudyNotesResponse


class TestNoteModel:
    
    def test_valid_note(self):
        note_data = {
            "id": 1,
            "heading": "Mean Value Theorem",
            "summary": "States that for continuous functions on [a,b], there exists c where f'(c) = (f(b)-f(a))/(b-a).",
            "page_ref": 42,
            "topic_area": "Calculus Theorems",
            "difficulty": "Intermediate"
        }
        
        note = Note(**note_data)
        assert note.id == 1
        assert note.heading == "Mean Value Theorem"
        assert note.page_ref == 42
        assert note.difficulty == "Intermediate"
    
    def test_note_without_page_ref(self):
        note_data = {
            "id": 2,
            "heading": "Power Rule",
            "summary": "d/dx(x^n) = nx^(n-1) for any real number n.",
            "page_ref": None,
            "topic_area": "Derivative Rules",
            "difficulty": "Basic"
        }
        
        note = Note(**note_data)
        assert note.page_ref is None
    
    def test_invalid_id_range(self):
        with pytest.raises(ValidationError) as exc_info:
            Note(
                id=0,
                heading="Test",
                summary="Test summary",
                topic_area="Test",
                difficulty="Basic"
            )
        assert "greater than or equal to 1" in str(exc_info.value)
        
        with pytest.raises(ValidationError) as exc_info:
            Note(
                id=11,
                heading="Test",
                summary="Test summary",
                topic_area="Test",
                difficulty="Basic"
            )
        assert "less than or equal to 10" in str(exc_info.value)
    
    def test_heading_length_constraints(self):
        with pytest.raises(ValidationError) as exc_info:
            Note(
                id=1,
                heading="A",
                summary="Test summary",
                topic_area="Test",
                difficulty="Basic"
            )
        assert "at least 5 characters" in str(exc_info.value)
        
        with pytest.raises(ValidationError) as exc_info:
            Note(
                id=1,
                heading="A" * 101,
                summary="Test summary",
                topic_area="Test",
                difficulty="Basic"
            )
        assert "at most 100 characters" in str(exc_info.value)
    
    def test_summary_length_constraint(self):
        with pytest.raises(ValidationError) as exc_info:
            Note(
                id=1,
                heading="Test Heading",
                summary="A" * 151,
                topic_area="Test",
                difficulty="Basic"
            )
        assert "at most 150 characters" in str(exc_info.value)
    
    def test_required_fields(self):
        with pytest.raises(ValidationError) as exc_info:
            Note(id=1)
        
        errors = str(exc_info.value)
        assert "heading" in errors
        assert "summary" in errors
        assert "topic_area" in errors
        assert "difficulty" in errors


class TestStudyNotesResponse:
    
    def test_valid_response(self):
        notes_data = []
        for i in range(1, 11):
            notes_data.append({
                "id": i,
                "heading": f"Concept {i}",
                "summary": f"Summary for concept {i}.",
                "page_ref": i * 10 if i % 2 == 0 else None,
                "topic_area": "Calculus",
                "difficulty": "Basic"
            })
        
        response_data = {
            "notes": notes_data,
            "total_count": 10,
            "subject": "Calculus"
        }
        
        response = StudyNotesResponse(**response_data)
        assert len(response.notes) == 10
        assert response.total_count == 10
        assert response.subject == "Calculus"
    
    def test_wrong_number_of_notes(self):
        notes_data = [
            {
                "id": 1,
                "heading": "Single Note",
                "summary": "Just one note.",
                "topic_area": "Test",
                "difficulty": "Basic"
            }
        ]
        
        with pytest.raises(ValidationError) as exc_info:
            StudyNotesResponse(
                notes=notes_data,
                total_count=10,
                subject="Test"
            )
        assert "at least 10 items" in str(exc_info.value)
        
        notes_data = []
        for i in range(1, 12):
            notes_data.append({
                "id": i if i <= 10 else 10,
                "heading": f"Note {i}",
                "summary": f"Summary {i}.",
                "topic_area": "Test",
                "difficulty": "Basic"
            })
        
        with pytest.raises(ValidationError) as exc_info:
            StudyNotesResponse(
                notes=notes_data,
                total_count=10,
                subject="Test"
            )
        assert "at most 10 items" in str(exc_info.value)


class TestJSONSerialization:
    
    def test_model_to_json(self):
        note = Note(
            id=1,
            heading="Test Note",
            summary="A test summary.",
            page_ref=5,
            topic_area="Testing",
            difficulty="Basic"
        )
        
        note_dict = note.model_dump()
        assert isinstance(note_dict, dict)
        assert note_dict["id"] == 1
        assert note_dict["heading"] == "Test Note"
        
        json_str = json.dumps(note_dict)
        assert isinstance(json_str, str)
        
        parsed_dict = json.loads(json_str)
        reconstructed_note = Note(**parsed_dict)
        assert reconstructed_note.id == note.id
        assert reconstructed_note.heading == note.heading
    
    def test_complete_response_json(self):
        notes = []
        for i in range(1, 11):
            notes.append(Note(
                id=i,
                heading=f"Concept {i}",
                summary=f"Summary {i}.",
                topic_area="Math",
                difficulty="Basic"
            ))
        
        response = StudyNotesResponse(
            notes=notes,
            total_count=10,
            subject="Mathematics"
        )
        
        response_dict = response.model_dump()
        json_str = json.dumps(response_dict, indent=2)
        
        parsed_dict = json.loads(json_str)
        reconstructed_response = StudyNotesResponse(**parsed_dict)
        
        assert len(reconstructed_response.notes) == 10
        assert reconstructed_response.total_count == 10
        assert reconstructed_response.subject == "Mathematics"


class TestEdgeCases:
    
    def test_unicode_content(self):
        note = Note(
            id=1,
            heading="Théorème de la Valeur Moyenne",
            summary="Énoncé: Pour une fonction continue... ∫∂∇∑",
            topic_area="Théorèmes",
            difficulty="Intermediate"
        )
        
        assert "Théorème" in note.heading
        assert "∫∂∇∑" in note.summary
    
    def test_boundary_values(self):
        note = Note(
            id=1,
            heading="12345",
            summary="Minimum length heading test.",
            topic_area="Test",
            difficulty="Basic"
        )
        assert len(note.heading) == 5
        
        long_heading = "A" * 100
        note = Note(
            id=1,
            heading=long_heading,
            summary="Maximum length heading test.",
            topic_area="Test", 
            difficulty="Basic"
        )
        assert len(note.heading) == 100
        
        long_summary = "B" * 150
        note = Note(
            id=1,
            heading="Test Heading",
            summary=long_summary,
            topic_area="Test",
            difficulty="Basic"
        )
        assert len(note.summary) == 150


def create_sample_notes():
    return [
        Note(
            id=1,
            heading="Limit Definition",
            summary="The limit of f(x) as x approaches a is L if f(x) can be made arbitrarily close to L.",
            page_ref=15,
            topic_area="Limits",
            difficulty="Basic"
        ),
        Note(
            id=2,
            heading="Mean Value Theorem",
            summary="For continuous f on [a,b], there exists c where f'(c) = (f(b)-f(a))/(b-a).",
            page_ref=87,
            topic_area="Theorems",
            difficulty="Intermediate"
        ),
        Note(
            id=3,
            heading="Integration by Parts",
            summary="∫u dv = uv - ∫v du. Used when integrand is a product of functions.",
            page_ref=203,
            topic_area="Integration",
            difficulty="Advanced"
        )
    ]


if __name__ == "__main__":
    print("Running basic schema validation tests...")
    
    try:
        sample_notes = create_sample_notes()
        print(f"✅ Created {len(sample_notes)} sample notes")
        
        all_notes = sample_notes.copy()
        for i in range(4, 11):
            all_notes.append(Note(
                id=i,
                heading=f"Concept {i}",
                summary=f"Description of concept {i}.",
                topic_area="General",
                difficulty="Basic"
            ))
        
        response = StudyNotesResponse(
            notes=all_notes,
            total_count=10,
            subject="Calculus"
        )
        print(f"✅ Created complete response with {len(response.notes)} notes")
        
        json_output = json.dumps(response.model_dump(), indent=2)
        print("✅ JSON serialization successful")
        
        print("\n📝 All basic tests passed! Run 'pytest tests/test_notes_schema.py -v' for full test suite.")
        
    except Exception as e:
        print(f"❌ Error in basic tests: {e}") 