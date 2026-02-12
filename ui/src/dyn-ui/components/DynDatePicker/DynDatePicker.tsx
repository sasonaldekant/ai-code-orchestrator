import React, {
  forwardRef,
  useCallback,
  useEffect,
  useId,
  useImperativeHandle,
  useMemo,
  useRef,
  useState,
} from 'react';
import type { ChangeEvent, KeyboardEvent, FocusEvent } from 'react';
import { cn } from '../../utils/classNames';
import type {
  DynDatePickerProps,
  DynDatePickerRef,
  DynDatePickerSize
} from './DynDatePicker.types';
import { DYN_DATE_PICKER_DEFAULT_PROPS } from './DynDatePicker.types';
import { DynFieldContainer } from '../DynFieldContainer';
import { useDynFieldValidation } from '../../hooks/useDynFieldValidation';
import { useDynDateParser } from '../../hooks/useDynDateParser';
import { DynIcon } from '../DynIcon';
import { DynDropdown } from '../DynDropdown';
import styles from './DynDatePicker.module.css';

const MAX_DATE_LENGTH = 10;

const DEFAULT_MONTH_NAMES = [
  'januar', 'februar', 'mart', 'april', 'maj', 'jun',
  'jul', 'avgust', 'septembar', 'oktobar', 'novembar', 'decembar'
];

const DEFAULT_WEEKDAY_NAMES = ['ne', 'po', 'ut', 'sr', 'če', 'pe', 'su'];

const sizeClassMap: Record<DynDatePickerSize, string | undefined> = {
  sm: styles['sizeSm'],
  md: styles['sizeMd'],
  lg: styles['sizeLg'],
};

// Helper: Get days in month
const getDaysInMonth = (year: number, month: number): number => {
  return new Date(year, month + 1, 0).getDate();
};

// Helper: Get first day of month (0 = Sunday, 1 = Monday, etc.)
const getFirstDayOfMonth = (year: number, month: number): number => {
  return new Date(year, month, 1).getDay();
};

// Helper: Check if two dates are the same day
const isSameDay = (a: Date | null, b: Date | null): boolean => {
  if (!a || !b) return false;
  return a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate();
};

// Helper: Check if date is today
const isToday = (date: Date): boolean => {
  return isSameDay(date, new Date());
};

export const DynDatePicker = forwardRef<DynDatePickerRef, DynDatePickerProps>(
  (
    {
      id: idProp,
      name,
      label,
      help,
      helpText,
      placeholder = 'dd/mm/yyyy',
      disabled = false,
      readonly = false,
      required = false,
      optional = false,
      visible = DYN_DATE_PICKER_DEFAULT_PROPS.visible,
      value: propValue,
      errorMessage,
      errorText: errorMessageText,
      validation,
      className,
      size = DYN_DATE_PICKER_DEFAULT_PROPS.size,
      onChange,
      onBlur,
      onFocus,
      min,
      max,
      weekStartsOn = DYN_DATE_PICKER_DEFAULT_PROPS.weekStartsOn,
      todayText = DYN_DATE_PICKER_DEFAULT_PROPS.todayText,
      clearText = DYN_DATE_PICKER_DEFAULT_PROPS.clearText,
      monthNames = DEFAULT_MONTH_NAMES,
      weekdayNames = DEFAULT_WEEKDAY_NAMES,
      'data-testid': dataTestId = 'dyn-date-picker',
      format = 'dd/MM/yyyy',
      ...rest
    },
    ref
  ) => {
    const instanceId = useId();
    const inputId = idProp ?? name ?? instanceId;
    const dropdownId = `${inputId}-dropdown`;
    const calendarGridId = `${inputId}-calendar-grid`;

    const resolvedHelpText = helpText ?? help;
    const resolvedErrorText = errorMessageText ?? errorMessage;

    const triggerRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    const [value, setValue] = useState<Date | null>(null);
    const [isOpen, setIsOpen] = useState(false);
    const [focused, setFocused] = useState(false);
    const [viewDate, setViewDate] = useState<Date>(new Date());
    const [focusedDay, setFocusedDay] = useState<Date | null>(null);

    const locale = 'en-US';

    const { error, validate, clearError } = useDynFieldValidation({
      value,
      required,
      validation: [],
      customError: resolvedErrorText,
    });

    const {
      displayValue,
      setDisplayValue,
      formatDate,
      parseDate,
      isValidDate,
      getRelativeDescription,
    } = useDynDateParser({
      format,
      locale,
    });

    // Parse min/max dates
    const minDate = useMemo(() => (min ? new Date(min) : null), [min]);
    const maxDate = useMemo(() => (max ? new Date(max) : null), [max]);

    // Check if a date is within the allowed range
    const isDateInRange = useCallback((date: Date): boolean => {
      if (minDate && date < minDate) return false;
      if (maxDate && date > maxDate) return false;
      return true;
    }, [minDate, maxDate]);

    const parseExternalValue = useCallback(
      (input: string | undefined): Date | null => {
        if (!input) return null;
        const candidate = new Date(input);
        return isValidDate(candidate) ? candidate : null;
      },
      [isValidDate]
    );

    useEffect(() => {
      const nextValue = parseExternalValue(propValue);
      setValue(nextValue);

      // Update display value only if:
      // 1. We are not focused (external update or blur)
      // 2. Or if we have a valid date (auto-format)
      // This prevents clearing the input while the user is typing a partial date
      if (!focused || nextValue !== null) {
        setDisplayValue(nextValue ? formatDate(nextValue) : '');
      }

      if (nextValue) {
        setViewDate(nextValue);
      }
    }, [propValue, formatDate, parseExternalValue, setDisplayValue, focused]);

    useImperativeHandle(ref, () => ({
      focus: () => inputRef.current?.focus(),
      blur: () => inputRef.current?.blur(),
      validate: () => validate(),
      clear: () => {
        setValue(null);
        setDisplayValue('');
        onChange?.('');
        clearError();
      },
      getValue: () => (value ? value.toISOString().split('T')[0] : undefined),
    }), [validate, value, clearError, onChange, setDisplayValue]);

    const emitChange = useCallback(
      (nextValue: Date | null) => {
        setValue(nextValue);
        setDisplayValue(nextValue ? formatDate(nextValue) : '');
        onChange?.(nextValue ? nextValue.toISOString().split('T')[0] : '');
      },
      [formatDate, onChange, setDisplayValue]
    );

    const handleInputChange = useCallback(
      (event: ChangeEvent<HTMLInputElement>) => {
        const inputValue = event.target.value;
        setDisplayValue(inputValue);

        const parsedDate = parseDate(inputValue);
        if (parsedDate && isValidDate(parsedDate)) {
          emitChange(parsedDate);
          clearError();
        } else if (!inputValue) {
          emitChange(null);
          clearError();
        }
      },
      [parseDate, isValidDate, emitChange, clearError, setDisplayValue]
    );

    const handleDayClick = useCallback((day: Date) => {
      if (!isDateInRange(day)) return;
      emitChange(day);
      clearError();
      setIsOpen(false);
      inputRef.current?.focus();
    }, [emitChange, clearError, isDateInRange]);

    const handleTodayClick = useCallback(() => {
      const today = new Date();
      if (!isDateInRange(today)) return;
      emitChange(today);
      clearError();
      setIsOpen(false);
    }, [emitChange, clearError, isDateInRange]);

    const handleClearClick = useCallback((e: React.MouseEvent) => {
      e.stopPropagation();
      emitChange(null);
      clearError();
      inputRef.current?.focus();
    }, [emitChange, clearError]);

    const handlePrevMonth = useCallback(() => {
      setViewDate(prev => new Date(prev.getFullYear(), prev.getMonth() - 1, 1));
    }, []);

    const handleNextMonth = useCallback(() => {
      setViewDate(prev => new Date(prev.getFullYear(), prev.getMonth() + 1, 1));
    }, []);

    const handleBlur = useCallback((e: FocusEvent<HTMLInputElement>) => {
      setFocused(false);
      validate();
      onBlur?.(e);
    }, [validate, onBlur]);

    const handleFocus = useCallback((e: FocusEvent<HTMLInputElement>) => {
      setFocused(true);
      clearError();
      onFocus?.(e);
    }, [clearError, onFocus]);

    const handleKeyDown = useCallback(
      (event: KeyboardEvent<HTMLInputElement>) => {
        switch (event.key) {
          case 'Enter':
          case 'ArrowDown':
            if (!isOpen) {
              setIsOpen(true);
              event.preventDefault();
            }
            break;
          case 'Escape':
            if (isOpen) {
              setIsOpen(false);
              event.preventDefault();
            }
            break;
          default:
            break;
        }
      },
      [isOpen]
    );

    // Generate calendar days
    const calendarDays = useMemo(() => {
      const year = viewDate.getFullYear();
      const month = viewDate.getMonth();
      const daysInMonth = getDaysInMonth(year, month);
      const firstDay = getFirstDayOfMonth(year, month);

      // Adjust for week start
      const startOffset = (firstDay - weekStartsOn + 7) % 7;

      const days: Array<{ date: Date; isCurrentMonth: boolean }> = [];

      // Previous month days
      const prevMonth = month === 0 ? 11 : month - 1;
      const prevYear = month === 0 ? year - 1 : year;
      const daysInPrevMonth = getDaysInMonth(prevYear, prevMonth);

      for (let i = startOffset - 1; i >= 0; i--) {
        days.push({
          date: new Date(prevYear, prevMonth, daysInPrevMonth - i),
          isCurrentMonth: false,
        });
      }

      // Current month days
      for (let i = 1; i <= daysInMonth; i++) {
        days.push({
          date: new Date(year, month, i),
          isCurrentMonth: true,
        });
      }

      // Next month days to fill the grid (6 rows * 7 days = 42)
      const remainingDays = 42 - days.length;
      const nextMonth = month === 11 ? 0 : month + 1;
      const nextYear = month === 11 ? year + 1 : year;

      for (let i = 1; i <= remainingDays; i++) {
        days.push({
          date: new Date(nextYear, nextMonth, i),
          isCurrentMonth: false,
        });
      }

      return days;
    }, [viewDate, weekStartsOn]);

    // Reorder weekday names based on weekStartsOn
    const orderedWeekdays = useMemo(() => {
      const reordered = [...weekdayNames];
      if (weekStartsOn === 1) {
        const sunday = reordered.shift();
        if (sunday) reordered.push(sunday);
      }
      return reordered;
    }, [weekdayNames, weekStartsOn]);

    if (!visible) return null;

    const fieldError = resolvedErrorText ?? (error || undefined);

    const containerClasses = cn(
      styles.container,
      sizeClassMap[size],
      className
    );

    const inputClasses = cn(
      styles.input,
      focused && styles.stateFocused,
      Boolean(fieldError) && styles.stateError,
      disabled && styles.stateDisabled,
      readonly && styles.stateReadonly,
      isOpen && styles.stateOpen
    );

    const relativeText = useMemo(
      () => (value ? getRelativeDescription(value) : null),
      [value, getRelativeDescription]
    );

    const monthYearLabel = `${monthNames[viewDate.getMonth()]} ${viewDate.getFullYear()}.`;

    return (
      <DynFieldContainer
        label={label}
        helpText={resolvedHelpText}
        required={required}
        optional={optional}
        errorText={fieldError}
        className={className}
        htmlFor={inputId}
      >
        <div ref={triggerRef} className={containerClasses} data-testid={dataTestId} style={rest.style}>
          <DynDropdown
            isOpen={isOpen}
            onOpenChange={setIsOpen}
            disabled={disabled}
            triggerWrapper="div"
            triggerRole="presentation"
            fullWidth={true}
            trigger={
              <div className={styles.inputContainer}>
                <input
                  ref={inputRef}
                  id={inputId}
                  name={name ?? inputId}
                  type="text"
                  role="combobox"
                  className={inputClasses}
                  placeholder={placeholder}
                  value={displayValue}
                  disabled={disabled}
                  readOnly={readonly}
                  onChange={handleInputChange}
                  onBlur={handleBlur}
                  onFocus={handleFocus}
                  onKeyDown={handleKeyDown}
                  aria-invalid={Boolean(fieldError)}
                  aria-haspopup="grid"
                  aria-expanded={isOpen}
                  aria-controls={isOpen ? calendarGridId : undefined}
                  aria-autocomplete="none"
                  maxLength={MAX_DATE_LENGTH}
                  data-size={size}
                  {...rest}
                />

                <div className={styles.inputActions}>
                  {displayValue && !readonly && !disabled && (
                    <button
                      type="button"
                      className={styles.clearButton}
                      onClick={handleClearClick}
                      tabIndex={-1}
                      aria-label={clearText}
                    >
                      <DynIcon icon="close" size="sm" />
                    </button>
                  )}
                  <div className={styles.calendarIcon}>
                    <DynIcon icon="calendar" size="sm" />
                  </div>
                </div>
              </div>
            }
            placement="bottom-start"
            offset={4}
            usePortal={true}
            aria-label="Open calendar"
          >
            <div id={dropdownId} className={styles.dropdown} role="dialog" aria-label="Date picker">
              {/* Calendar Header */}
              <div className={styles.calendarHeader}>
                <button
                  type="button"
                  className={styles.navButton}
                  onClick={handlePrevMonth}
                  aria-label="Previous month"
                >
                  <DynIcon icon="chevron-left" size="sm" />
                </button>
                <div className={styles.headerSelectWrapper}>
                  <select
                    value={viewDate.getMonth()}
                    onChange={(e) => {
                      e.stopPropagation();
                      const newMonth = parseInt(e.target.value, 10);
                      setViewDate(prev => new Date(prev.getFullYear(), newMonth, 1));
                    }}
                    className={styles.headerSelect}
                    aria-label="Select month"
                    onClick={(e) => e.stopPropagation()}
                  >
                    {monthNames.map((name, i) => (
                      <option key={i} value={i}>{name}</option>
                    ))}
                  </select>
                  <select
                    value={viewDate.getFullYear()}
                    onChange={(e) => {
                      e.stopPropagation();
                      const newYear = parseInt(e.target.value, 10);
                      setViewDate(prev => new Date(newYear, prev.getMonth(), 1));
                    }}
                    className={styles.headerSelect}
                    aria-label="Select year"
                    onClick={(e) => e.stopPropagation()}
                  >
                    {Array.from({ length: 120 }, (_, i) => new Date().getFullYear() - 100 + i).map(year => (
                      <option key={year} value={year}>{year}</option>
                    ))}
                  </select>
                </div>
                <button
                  type="button"
                  className={styles.navButton}
                  onClick={handleNextMonth}
                  aria-label="Next month"
                >
                  <DynIcon icon="chevron-right" size="sm" />
                </button>
              </div>

              {/* Weekday Headers */}
              <div className={styles.weekdays} role="row">
                {orderedWeekdays.map((day, index) => (
                  <div key={index} className={styles.weekday} role="columnheader">
                    {day}
                  </div>
                ))}
              </div>

              {/* Calendar Grid */}
              <div
                id={calendarGridId}
                className={styles.calendarGrid}
                role="grid"
                aria-label={monthYearLabel}
              >
                {calendarDays.map(({ date, isCurrentMonth }, index) => {
                  const isSelected = isSameDay(date, value);
                  const isTodayDate = isToday(date);
                  const isDisabled = !isDateInRange(date);

                  return (
                    <button
                      key={index}
                      type="button"
                      role="gridcell"
                      className={cn(
                        styles.day,
                        !isCurrentMonth && styles.dayOutside,
                        isTodayDate && styles.dayToday,
                        isSelected && styles.daySelected,
                        isDisabled && styles.dayDisabled
                      )}
                      onClick={() => handleDayClick(date)}
                      disabled={isDisabled}
                      tabIndex={isSelected ? 0 : -1}
                      aria-selected={isSelected}
                      aria-label={date.toLocaleDateString()}
                    >
                      {date.getDate()}
                    </button>
                  );
                })}
              </div>

              {/* Shortcuts */}
              <div className={styles.shortcuts}>
                <button type="button" className={styles.shortcut} onClick={handleTodayClick}>
                  {todayText}
                </button>
                <button type="button" className={styles.shortcut} onClick={(e) => handleClearClick(e)}>
                  {clearText}
                </button>
              </div>
            </div>
          </DynDropdown>

          {relativeText && <div className={styles.relativeText}>{relativeText}</div>}
        </div>
      </DynFieldContainer>
    );
  }
);

DynDatePicker.displayName = 'DynDatePicker';
export default DynDatePicker;
