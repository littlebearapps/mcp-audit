"""
Tests for the modal dialog system.

Tests Modal base class and all modal variants:
- SelectModal: Radio button selection
- ConfirmModal: Yes/No confirmation
- InputModal: Text input with validation

v1.0.3 - task-233.15
"""

import pytest
from rich import box

from token_audit.display.keyboard import KEY_BACKSPACE, KEY_DOWN, KEY_ENTER, KEY_ESC, KEY_UP
from token_audit.display.modals import (
    ConfirmModal,
    InputModal,
    InputValidation,
    Modal,
    ModalOption,
    ModalResult,
    SelectModal,
    create_date_range_input_modal,
    create_delete_confirm_modal,
    create_platform_select_modal,
)
from token_audit.display.themes import CatppuccinMocha, CatppuccinLatte


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def dark_theme() -> CatppuccinMocha:
    """Provide dark theme for tests."""
    return CatppuccinMocha()


@pytest.fixture
def light_theme() -> CatppuccinLatte:
    """Provide light theme for tests."""
    return CatppuccinLatte()


@pytest.fixture
def sample_options() -> list[ModalOption]:
    """Provide sample options for SelectModal tests."""
    return [
        ModalOption(label="Option 1", description="First option", value="opt1"),
        ModalOption(label="Option 2", description="Second option", value="opt2"),
        ModalOption(label="Option 3", description="Third option", value="opt3"),
    ]


# ============================================================================
# ModalOption Tests
# ============================================================================


class TestModalOption:
    """Tests for ModalOption dataclass."""

    def test_option_with_all_fields(self) -> None:
        """Test creating option with all fields."""
        opt = ModalOption(label="Test", description="Description", value="val")
        assert opt.label == "Test"
        assert opt.description == "Description"
        assert opt.value == "val"

    def test_option_value_defaults_to_label(self) -> None:
        """Test that value defaults to label when not provided."""
        opt = ModalOption(label="Test Label")
        assert opt.value == "Test Label"

    def test_option_empty_description(self) -> None:
        """Test option with empty description."""
        opt = ModalOption(label="Test", value="val")
        assert opt.description == ""


# ============================================================================
# ModalResult Tests
# ============================================================================


class TestModalResult:
    """Tests for ModalResult dataclass."""

    def test_dismissed_result(self) -> None:
        """Test creating dismissed result."""
        result = ModalResult(dismissed=True, confirmed=False)
        assert result.dismissed is True
        assert result.confirmed is False
        assert result.value is None

    def test_confirmed_result_with_value(self) -> None:
        """Test creating confirmed result with value."""
        result = ModalResult(dismissed=False, confirmed=True, value="selected")
        assert result.dismissed is False
        assert result.confirmed is True
        assert result.value == "selected"


# ============================================================================
# SelectModal Tests
# ============================================================================


class TestSelectModal:
    """Tests for SelectModal class."""

    def test_create_with_options(
        self, dark_theme: CatppuccinMocha, sample_options: list[ModalOption]
    ) -> None:
        """Test creating SelectModal with options."""
        modal = SelectModal(
            title="Test Modal",
            options=sample_options,
            theme=dark_theme,
        )
        assert modal.title == "Test Modal"
        assert len(modal.options) == 3
        assert modal.selected_index == 0

    def test_initial_selected_index(
        self, dark_theme: CatppuccinMocha, sample_options: list[ModalOption]
    ) -> None:
        """Test setting initial selected index."""
        modal = SelectModal(
            title="Test",
            options=sample_options,
            theme=dark_theme,
            selected_index=2,
        )
        assert modal.selected_index == 2

    def test_selected_index_clamped_to_options(
        self, dark_theme: CatppuccinMocha, sample_options: list[ModalOption]
    ) -> None:
        """Test that selected index is clamped to valid range."""
        modal = SelectModal(
            title="Test",
            options=sample_options,
            theme=dark_theme,
            selected_index=10,  # Out of range
        )
        assert modal.selected_index == 2  # Clamped to last option

    def test_build_returns_panel(
        self, dark_theme: CatppuccinMocha, sample_options: list[ModalOption]
    ) -> None:
        """Test that build returns a Rich Panel."""
        modal = SelectModal(title="Test", options=sample_options, theme=dark_theme)
        panel = modal.build()
        assert panel is not None
        assert panel.title == "Test"

    def test_esc_dismisses_modal(
        self, dark_theme: CatppuccinMocha, sample_options: list[ModalOption]
    ) -> None:
        """Test ESC key dismisses modal."""
        modal = SelectModal(title="Test", options=sample_options, theme=dark_theme)
        should_close, result = modal.handle_key(KEY_ESC)
        assert should_close is True
        assert result.dismissed is True
        assert result.confirmed is False

    def test_enter_confirms_selection(
        self, dark_theme: CatppuccinMocha, sample_options: list[ModalOption]
    ) -> None:
        """Test Enter key confirms selection."""
        modal = SelectModal(title="Test", options=sample_options, theme=dark_theme)
        should_close, result = modal.handle_key(KEY_ENTER)
        assert should_close is True
        assert result.confirmed is True
        assert result.value == "opt1"  # First option

    def test_j_key_moves_down(
        self, dark_theme: CatppuccinMocha, sample_options: list[ModalOption]
    ) -> None:
        """Test j key moves selection down."""
        modal = SelectModal(title="Test", options=sample_options, theme=dark_theme)
        assert modal.selected_index == 0
        modal.handle_key("j")
        assert modal.selected_index == 1

    def test_k_key_moves_up(
        self, dark_theme: CatppuccinMocha, sample_options: list[ModalOption]
    ) -> None:
        """Test k key moves selection up."""
        modal = SelectModal(
            title="Test", options=sample_options, theme=dark_theme, selected_index=1
        )
        modal.handle_key("k")
        assert modal.selected_index == 0

    def test_down_arrow_moves_down(
        self, dark_theme: CatppuccinMocha, sample_options: list[ModalOption]
    ) -> None:
        """Test down arrow moves selection down."""
        modal = SelectModal(title="Test", options=sample_options, theme=dark_theme)
        modal.handle_key(KEY_DOWN)
        assert modal.selected_index == 1

    def test_up_arrow_moves_up(
        self, dark_theme: CatppuccinMocha, sample_options: list[ModalOption]
    ) -> None:
        """Test up arrow moves selection up."""
        modal = SelectModal(
            title="Test", options=sample_options, theme=dark_theme, selected_index=2
        )
        modal.handle_key(KEY_UP)
        assert modal.selected_index == 1

    def test_navigation_wraps_around(
        self, dark_theme: CatppuccinMocha, sample_options: list[ModalOption]
    ) -> None:
        """Test navigation wraps from last to first."""
        modal = SelectModal(
            title="Test", options=sample_options, theme=dark_theme, selected_index=2
        )
        modal.handle_key("j")
        assert modal.selected_index == 0  # Wrapped to first

    def test_navigation_wraps_up(
        self, dark_theme: CatppuccinMocha, sample_options: list[ModalOption]
    ) -> None:
        """Test navigation wraps from first to last."""
        modal = SelectModal(title="Test", options=sample_options, theme=dark_theme)
        modal.handle_key("k")
        assert modal.selected_index == 2  # Wrapped to last

    def test_number_key_quick_select(
        self, dark_theme: CatppuccinMocha, sample_options: list[ModalOption]
    ) -> None:
        """Test number keys 1-9 for quick selection."""
        modal = SelectModal(title="Test", options=sample_options, theme=dark_theme)
        should_close, result = modal.handle_key("2")
        assert should_close is True
        assert result.confirmed is True
        assert result.value == "opt2"

    def test_number_key_out_of_range_ignored(
        self, dark_theme: CatppuccinMocha, sample_options: list[ModalOption]
    ) -> None:
        """Test number keys beyond options are ignored."""
        modal = SelectModal(title="Test", options=sample_options, theme=dark_theme)
        should_close, result = modal.handle_key("9")  # Only 3 options
        assert should_close is False
        assert result.confirmed is False

    def test_unrecognized_key_ignored(
        self, dark_theme: CatppuccinMocha, sample_options: list[ModalOption]
    ) -> None:
        """Test unrecognized keys are ignored."""
        modal = SelectModal(title="Test", options=sample_options, theme=dark_theme)
        should_close, result = modal.handle_key("x")
        assert should_close is False
        assert result.confirmed is False

    def test_empty_options_list(self, dark_theme: CatppuccinMocha) -> None:
        """Test handling empty options list."""
        modal = SelectModal(title="Test", options=[], theme=dark_theme)
        assert modal.selected_index == 0
        # Should not crash on Enter
        should_close, result = modal.handle_key(KEY_ENTER)
        assert should_close is True
        assert result.value is None


# ============================================================================
# ConfirmModal Tests
# ============================================================================


class TestConfirmModal:
    """Tests for ConfirmModal class."""

    def test_create_confirm_modal(self, dark_theme: CatppuccinMocha) -> None:
        """Test creating ConfirmModal."""
        modal = ConfirmModal(
            title="Confirm",
            message="Are you sure?",
            theme=dark_theme,
        )
        assert modal.title == "Confirm"
        assert modal.message == "Are you sure?"
        assert modal.selected_yes is False  # Default to No

    def test_danger_mode(self, dark_theme: CatppuccinMocha) -> None:
        """Test danger mode styling."""
        modal = ConfirmModal(
            title="Delete",
            message="Delete item?",
            theme=dark_theme,
            danger=True,
        )
        assert modal.danger is True
        panel = modal.build()
        assert panel is not None

    def test_custom_button_labels(self, dark_theme: CatppuccinMocha) -> None:
        """Test custom yes/no button labels."""
        modal = ConfirmModal(
            title="Delete",
            message="Delete?",
            theme=dark_theme,
            yes_label="Delete",
            no_label="Cancel",
        )
        assert modal.yes_label == "Delete"
        assert modal.no_label == "Cancel"

    def test_y_key_confirms(self, dark_theme: CatppuccinMocha) -> None:
        """Test y key confirms immediately."""
        modal = ConfirmModal(title="Test", message="Test?", theme=dark_theme)
        should_close, result = modal.handle_key("y")
        assert should_close is True
        assert result.confirmed is True
        assert result.value is True

    def test_uppercase_y_confirms(self, dark_theme: CatppuccinMocha) -> None:
        """Test Y key confirms."""
        modal = ConfirmModal(title="Test", message="Test?", theme=dark_theme)
        should_close, result = modal.handle_key("Y")
        assert should_close is True
        assert result.confirmed is True

    def test_n_key_cancels(self, dark_theme: CatppuccinMocha) -> None:
        """Test n key cancels."""
        modal = ConfirmModal(title="Test", message="Test?", theme=dark_theme)
        should_close, result = modal.handle_key("n")
        assert should_close is True
        assert result.dismissed is True
        assert result.value is False

    def test_esc_key_cancels(self, dark_theme: CatppuccinMocha) -> None:
        """Test ESC key cancels."""
        modal = ConfirmModal(title="Test", message="Test?", theme=dark_theme)
        should_close, result = modal.handle_key(KEY_ESC)
        assert should_close is True
        assert result.dismissed is True

    def test_enter_with_no_selected(self, dark_theme: CatppuccinMocha) -> None:
        """Test Enter with No selected (default) dismisses."""
        modal = ConfirmModal(title="Test", message="Test?", theme=dark_theme)
        assert modal.selected_yes is False
        should_close, result = modal.handle_key(KEY_ENTER)
        assert should_close is True
        assert result.dismissed is True
        assert result.confirmed is False

    def test_enter_with_yes_selected(self, dark_theme: CatppuccinMocha) -> None:
        """Test Enter with Yes selected confirms."""
        modal = ConfirmModal(title="Test", message="Test?", theme=dark_theme)
        modal.selected_yes = True
        should_close, result = modal.handle_key(KEY_ENTER)
        assert should_close is True
        assert result.confirmed is True

    def test_h_key_toggles_selection(self, dark_theme: CatppuccinMocha) -> None:
        """Test h key toggles between Yes/No."""
        modal = ConfirmModal(title="Test", message="Test?", theme=dark_theme)
        assert modal.selected_yes is False
        modal.handle_key("h")
        assert modal.selected_yes is True
        modal.handle_key("h")
        assert modal.selected_yes is False

    def test_l_key_toggles_selection(self, dark_theme: CatppuccinMocha) -> None:
        """Test l key toggles between Yes/No."""
        modal = ConfirmModal(title="Test", message="Test?", theme=dark_theme)
        modal.handle_key("l")
        assert modal.selected_yes is True


# ============================================================================
# InputModal Tests
# ============================================================================


class TestInputModal:
    """Tests for InputModal class."""

    def test_create_input_modal(self, dark_theme: CatppuccinMocha) -> None:
        """Test creating InputModal."""
        modal = InputModal(
            title="Enter Name",
            prompt="Name:",
            theme=dark_theme,
        )
        assert modal.title == "Enter Name"
        assert modal.prompt == "Name:"
        assert modal.value == ""

    def test_initial_value(self, dark_theme: CatppuccinMocha) -> None:
        """Test InputModal with initial value."""
        modal = InputModal(
            title="Test",
            prompt="Value:",
            theme=dark_theme,
            initial_value="hello",
        )
        assert modal.value == "hello"

    def test_placeholder(self, dark_theme: CatppuccinMocha) -> None:
        """Test InputModal with placeholder."""
        modal = InputModal(
            title="Test",
            prompt="Value:",
            theme=dark_theme,
            placeholder="Type here...",
        )
        assert modal.placeholder == "Type here..."

    def test_typing_adds_characters(self, dark_theme: CatppuccinMocha) -> None:
        """Test typing printable characters."""
        modal = InputModal(title="Test", prompt="Value:", theme=dark_theme)
        modal.handle_key("h")
        modal.handle_key("e")
        modal.handle_key("l")
        modal.handle_key("l")
        modal.handle_key("o")
        assert modal.value == "hello"

    def test_backspace_removes_character(self, dark_theme: CatppuccinMocha) -> None:
        """Test backspace removes last character."""
        modal = InputModal(
            title="Test",
            prompt="Value:",
            theme=dark_theme,
            initial_value="hello",
        )
        modal.handle_key(KEY_BACKSPACE)
        assert modal.value == "hell"

    def test_backspace_on_empty_does_nothing(self, dark_theme: CatppuccinMocha) -> None:
        """Test backspace on empty string does nothing."""
        modal = InputModal(title="Test", prompt="Value:", theme=dark_theme)
        should_close, result = modal.handle_key(KEY_BACKSPACE)
        assert modal.value == ""
        assert should_close is False

    def test_ctrl_u_clears_input(self, dark_theme: CatppuccinMocha) -> None:
        """Test Ctrl+U clears all input."""
        modal = InputModal(
            title="Test",
            prompt="Value:",
            theme=dark_theme,
            initial_value="hello world",
        )
        modal.handle_key("\x15")  # Ctrl+U
        assert modal.value == ""

    def test_esc_cancels(self, dark_theme: CatppuccinMocha) -> None:
        """Test ESC key cancels."""
        modal = InputModal(
            title="Test",
            prompt="Value:",
            theme=dark_theme,
            initial_value="hello",
        )
        should_close, result = modal.handle_key(KEY_ESC)
        assert should_close is True
        assert result.dismissed is True

    def test_enter_submits_value(self, dark_theme: CatppuccinMocha) -> None:
        """Test Enter submits current value."""
        modal = InputModal(
            title="Test",
            prompt="Value:",
            theme=dark_theme,
            initial_value="hello",
        )
        should_close, result = modal.handle_key(KEY_ENTER)
        assert should_close is True
        assert result.confirmed is True
        assert result.value == "hello"

    def test_validation_success(self, dark_theme: CatppuccinMocha) -> None:
        """Test successful validation on submit."""

        def validator(value: str) -> InputValidation:
            if len(value) >= 3:
                return InputValidation(valid=True)
            return InputValidation(valid=False, error_message="Too short")

        modal = InputModal(
            title="Test",
            prompt="Value:",
            theme=dark_theme,
            initial_value="hello",
            validator=validator,
        )
        should_close, result = modal.handle_key(KEY_ENTER)
        assert should_close is True
        assert result.confirmed is True

    def test_validation_failure(self, dark_theme: CatppuccinMocha) -> None:
        """Test failed validation on submit."""

        def validator(value: str) -> InputValidation:
            if len(value) >= 3:
                return InputValidation(valid=True)
            return InputValidation(valid=False, error_message="Too short")

        modal = InputModal(
            title="Test",
            prompt="Value:",
            theme=dark_theme,
            initial_value="hi",
            validator=validator,
        )
        should_close, result = modal.handle_key(KEY_ENTER)
        assert should_close is False  # Modal stays open
        assert result.confirmed is False
        assert modal.error_message == "Too short"

    def test_error_clears_on_typing(self, dark_theme: CatppuccinMocha) -> None:
        """Test error message clears when user types."""

        def validator(value: str) -> InputValidation:
            return InputValidation(valid=False, error_message="Error")

        modal = InputModal(
            title="Test",
            prompt="Value:",
            theme=dark_theme,
            validator=validator,
        )
        modal.handle_key(KEY_ENTER)  # Trigger error
        assert modal.error_message == "Error"
        modal.handle_key("a")  # Type character
        assert modal.error_message == ""


# ============================================================================
# Convenience Function Tests
# ============================================================================


class TestConvenienceFunctions:
    """Tests for modal factory functions."""

    def test_create_platform_select_modal(self, dark_theme: CatppuccinMocha) -> None:
        """Test platform selection modal factory."""
        modal = create_platform_select_modal(dark_theme)
        assert modal.title == "Select Platform"
        assert len(modal.options) == 3
        assert modal.options[0].value == "claude-code"
        assert modal.options[1].value == "codex-cli"
        assert modal.options[2].value == "gemini-cli"

    def test_create_delete_confirm_modal(self, dark_theme: CatppuccinMocha) -> None:
        """Test delete confirmation modal factory."""
        modal = create_delete_confirm_modal(
            session_info="Session: test-123\nTokens: 1,000",
            theme=dark_theme,
        )
        assert modal.title == "Delete Session"
        assert "test-123" in modal.message
        assert modal.danger is True
        assert modal.yes_label == "Delete"
        assert modal.no_label == "Cancel"

    def test_create_date_range_input_modal(self, dark_theme: CatppuccinMocha) -> None:
        """Test date range input modal factory."""
        modal = create_date_range_input_modal(dark_theme)
        assert modal.title == "Date Range"
        assert modal.validator is not None

    def test_date_range_validation_valid(self, dark_theme: CatppuccinMocha) -> None:
        """Test date range validation with valid date."""
        modal = create_date_range_input_modal(dark_theme, initial_value="2025-12-26")
        should_close, result = modal.handle_key(KEY_ENTER)
        assert should_close is True
        assert result.confirmed is True

    def test_date_range_validation_invalid(self, dark_theme: CatppuccinMocha) -> None:
        """Test date range validation with invalid date."""
        modal = create_date_range_input_modal(dark_theme, initial_value="not-a-date")
        should_close, result = modal.handle_key(KEY_ENTER)
        assert should_close is False
        assert modal.error_message == "Invalid date format. Use YYYY-MM-DD"

    def test_date_range_validation_empty_allowed(self, dark_theme: CatppuccinMocha) -> None:
        """Test date range validation allows empty value."""
        modal = create_date_range_input_modal(dark_theme)
        should_close, result = modal.handle_key(KEY_ENTER)
        assert should_close is True
        assert result.confirmed is True


# ============================================================================
# Theme Integration Tests
# ============================================================================


class TestThemeIntegration:
    """Tests for modal rendering with different themes."""

    def test_select_modal_dark_theme(
        self, dark_theme: CatppuccinMocha, sample_options: list[ModalOption]
    ) -> None:
        """Test SelectModal renders with dark theme."""
        modal = SelectModal(title="Test", options=sample_options, theme=dark_theme)
        panel = modal.build()
        assert panel is not None

    def test_select_modal_light_theme(
        self, light_theme: CatppuccinLatte, sample_options: list[ModalOption]
    ) -> None:
        """Test SelectModal renders with light theme."""
        modal = SelectModal(title="Test", options=sample_options, theme=light_theme)
        panel = modal.build()
        assert panel is not None

    def test_confirm_modal_dark_theme(self, dark_theme: CatppuccinMocha) -> None:
        """Test ConfirmModal renders with dark theme."""
        modal = ConfirmModal(title="Test", message="Test?", theme=dark_theme)
        panel = modal.build()
        assert panel is not None

    def test_input_modal_dark_theme(self, dark_theme: CatppuccinMocha) -> None:
        """Test InputModal renders with dark theme."""
        modal = InputModal(title="Test", prompt="Value:", theme=dark_theme)
        panel = modal.build()
        assert panel is not None

    def test_input_modal_with_error_renders(self, dark_theme: CatppuccinMocha) -> None:
        """Test InputModal with error message renders correctly."""
        modal = InputModal(title="Test", prompt="Value:", theme=dark_theme)
        modal.error_message = "This is an error"
        panel = modal.build()
        assert panel is not None
