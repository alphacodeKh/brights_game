<?php
/*
Plugin Name: Електронний Журнал
Plugin URI: 
Description: Плагін електронного журналу для навчальних закладів 
Version: 1.5
Author: Alphacode
Author URI: 
License: GPLv2 or later
Text Domain: electronic-journal
*/

if (!defined('ABSPATH')) {
    exit;
}

class Electronic_Journal {
    public function __construct() {
        add_action('init', [$this, 'register_post_types']);
        add_action('acf/init', [$this, 'create_custom_fields']);
        add_action('admin_menu', [$this, 'add_journal_menu']);
        add_shortcode('electronic_journal', [$this, 'journal_shortcode']);
        add_action('admin_enqueue_scripts', [$this, 'enqueue_admin_scripts']);
        add_action('admin_post_import_excel_grades', [$this, 'handle_excel_import']);
    }

    // Реєстрація типів постів
    public function register_post_types() {
        // Тип посту для учнів
        register_post_type('student', [
            'labels' => [
                'name' => 'Учні',
                'singular_name' => 'Учень',
                'add_new' => 'Додати учня',
                'add_new_item' => 'Додати нового учня',
                'edit_item' => 'Редагувати учня',
                'view_item' => 'Переглянути учня',
                'search_items' => 'Пошук учнів',
                'not_found' => 'Учнів не знайдено',
                'not_found_in_trash' => 'В кошику учнів не знайдено'
            ],
            'public' => true,
            'has_archive' => true,
            'show_in_menu' => true,
            'supports' => ['title', 'editor'],
            'rewrite' => [
                'slug' => 'students',
                'with_front' => true
            ],
            'menu_icon' => 'dashicons-groups',
            'menu_position' => 20
        ]);

        // Тип посту для класів
        register_post_type('school_class', [
            'labels' => [
                'name' => 'Класи',
                'singular_name' => 'Клас',
                'add_new' => 'Додати клас',
                'add_new_item' => 'Додати новий клас',
                'edit_item' => 'Редагувати клас',
                'view_item' => 'Переглянути клас',
                'search_items' => 'Пошук класів',
                'not_found' => 'Класів не знайдено'
            ],
            'public' => true,
            'has_archive' => true,
            'supports' => ['title'],
            'rewrite' => [
                'slug' => 'classes'
            ],
            'menu_icon' => 'dashicons-welcome-learn-more',
            'menu_position' => 21
        ]);

        // Тип посту для оцінок
        register_post_type('grade', [
            'labels' => [
                'name' => 'Оцінки',
                'singular_name' => 'Оцінка',
                'add_new' => 'Додати оцінку',
                'add_new_item' => 'Додати нову оцінку',
                'edit_item' => 'Редагувати оцінку',
                'search_items' => 'Пошук оцінок',
                'not_found' => 'Оцінок не знайдено'
            ],
            'public' => false,
            'show_ui' => true,
            'show_in_menu' => true,
            'supports' => ['title'],
            'menu_icon' => 'dashicons-star-filled',
            'menu_position' => 22
        ]);

        flush_rewrite_rules();
    }

    // Створення полів ACF
    public function create_custom_fields() {
        if (function_exists('acf_add_local_field_group')) {
            // Поля для учнів
            acf_add_local_field_group([
                'key' => 'student_details',
                'title' => 'Деталі учня',
                'fields' => [
                    [
                        'key' => 'student_class',
                        'label' => 'Клас',
                        'name' => 'school_class',
                        'type' => 'post_object',
                        'post_type' => 'school_class'
                    ],
                    [
                        'key' => 'student_birthdate',
                        'label' => 'Дата народження',
                        'name' => 'birthdate',
                        'type' => 'date_picker'
                    ]
                ],
                'location' => [
                    [
                        [
                            'param' => 'post_type',
                            'operator' => '==',
                            'value' => 'student'
                        ]
                    ]
                ]
            ]);

            // Поля для оцінок
            acf_add_local_field_group([
                'key' => 'grade_details',
                'title' => 'Деталі оцінки',
                'fields' => [
                    [
                        'key' => 'grade_student',
                        'label' => 'Учень',
                        'name' => 'student',
                        'type' => 'post_object',
                        'post_type' => 'student'
                    ],
                    [
                        'key' => 'grade_subject',
                        'label' => 'Предмет',
                        'name' => 'subject',
                        'type' => 'text'
                    ],
                    [
                        'key' => 'grade_value',
                        'label' => 'Оцінка',
                        'name' => 'value',
                        'type' => 'number',
                        'min' => 1,
                        'max' => 12
                    ],
                    [
                        'key' => 'grade_date',
                        'label' => 'Дата',
                        'name' => 'date',
                        'type' => 'date_picker'
                    ]
                ],
                'location' => [
                    [
                        [
                            'param' => 'post_type',
                            'operator' => '==',
                            'value' => 'grade'
                        ]
                    ]
                ]
            ]);
        }
    }

    // Додавання стилів адмін-панелі
    public function enqueue_admin_scripts($hook) {
        if ('toplevel_page_electronic-journal' !== $hook) {
            return;
        }
        wp_enqueue_style('electronic-journal-admin', plugins_url('css/admin.css', __FILE__));
    }

    // Додавання меню в адмін-панель
    public function add_journal_menu() {
        add_menu_page(
            'Електронний Журнал',
            'Електронний Журнал',
            'manage_options',
            'electronic-journal',
            [$this, 'journal_dashboard'],
            'dashicons-welcome-learn-more',
            30
        );
    }

    // Сторінка адмін-панелі
    public function journal_dashboard() {
        ?>
        <div class="wrap">
            <h1>Електронний Журнал</h1>
            
            <div class="excel-import-section">
                <h2>Імпорт оцінок з Excel</h2>
                <form method="post" action="<?php echo admin_url('admin-post.php'); ?>" enctype="multipart/form-data">
                    <input type="hidden" name="action" value="import_excel_grades">
                    <?php wp_nonce_field('import_excel_grades_nonce', 'excel_nonce'); ?>
                    
                    <table class="form-table">
                        <tr>
                            <th scope="row"><label for="excel_file">Файл Excel:</label></th>
                            <td>
                                <input type="file" name="excel_file" id="excel_file" accept=".xlsx,.xls" required>
                                <p class="description">Підтримувані формати: .xlsx, .xls</p>
                            </td>
                        </tr>
                    </table>

                    <p class="submit">
                        <input type="submit" name="submit" class="button button-primary" value="Імпортувати оцінки">
                    </p>
                </form>
            </div>

            <?php $this->display_import_results(); ?>
        </div>
        <?php
    }

    // Відображення результатів імпорту
    private function display_import_results() {
        if (!isset($_GET['import_status'])) {
            return;
        }

        $status = $_GET['import_status'];
        $class = 'notice ';
        $message = '';

        switch ($status) {
            case 'success':
                $class .= 'notice-success';
                $imported = intval($_GET['imported']);
                $message = sprintf('Успішно імпортовано %d оцінок', $imported);
                break;
            case 'error':
                $class .= 'notice-error';
                $error_message = isset($_GET['message']) ? urldecode($_GET['message']) : 'Невідома помилка';
                $message = sprintf('Помилка імпорту: %s', $error_message);
                break;
            case 'no_file':
                $class .= 'notice-error';
                $message = 'Будь ласка, виберіть файл для імпорту';
                break;
        }

        if ($message) {
            printf('<div class="%s"><p>%s</p></div>', esc_attr($class), esc_html($message));
        }
    }

    // Обробка імпорту Excel
    public function handle_excel_import() {
        if (!current_user_can('manage_options')) {
            wp_die('Недостатньо прав для виконання цієї дії');
        }

        check_admin_referer('import_excel_grades_nonce', 'excel_nonce');

        if (!isset($_FILES['excel_file'])) {
            wp_redirect(add_query_arg('import_status', 'no_file', admin_url('admin.php?page=electronic-journal')));
            exit;
        }

        try {
            require_once plugin_dir_path(__FILE__) . 'vendor/autoload.php';

            $upload = wp_handle_upload($_FILES['excel_file'], ['test_form' => false]);

            if (isset($upload['error'])) {
                throw new Exception($upload['error']);
            }

            $spreadsheet = \PhpOffice\PhpSpreadsheet\IOFactory::load($upload['file']);
            $worksheet = $spreadsheet->getActiveSheet();
            $rows = $worksheet->toArray();

            // Пропускаємо заголовок
            array_shift($rows);

            $imported = 0;
            foreach ($rows as $row) {
                if (empty($row[0])) continue;

                // Формат: Учень | Предмет | Оцінка | Дата
                $student_name = sanitize_text_field($row[0]);
                $subject = sanitize_text_field($row[1]);
                $grade_value = intval($row[2]);
                $date = sanitize_text_field($row[3]);

                // Знаходимо або створюємо учня
                $student = get_page_by_title($student_name, OBJECT, 'student');
                if (!$student) {
                    $student_id = wp_insert_post([
                        'post_title' => $student_name,
                        'post_type' => 'student',
                        'post_status' => 'publish'
                    ]);
                } else {
                    $student_id = $student->ID;
                }

                // Створюємо оцінку
                $grade_id = wp_insert_post([
                    'post_type' => 'grade',
                    'post_status' => 'publish',
                    'post_title' => sprintf('Оцінка для %s - %s', $student_name, $subject)
                ]);

                update_field('student', $student_id, $grade_id);
                update_field('subject', $subject, $grade_id);
                update_field('value', $grade_value, $grade_id);
                update_field('date', $date, $grade_id);

                $imported++;
            }

            unlink($upload['file']);
            wp_redirect(add_query_arg(['import_status' => 'success', 'imported' => $imported], admin_url('admin.php?page=electronic-journal')));
            exit;

        } catch (Exception $e) {
            wp_redirect(add_query_arg(['import_status' => 'error', 'message' => urlencode($e->getMessage())], admin_url('admin.php?page=electronic-journal')));
            exit;
        }
    }

    // Шорткод для відображення журналу
    public function journal_shortcode($atts) {
        ob_start();
        ?>
        <div class="electronic-journal">
            <h2>Електронний Журнал</h2>
            
            <?php
            $grades = get_posts([
                'post_type' => 'grade',
                'posts_per_page' => -1,
                'orderby' => 'date',
                'order' => 'DESC'
            ]);

            if ($grades): ?>
                <table class="journal-table">
                    <thead>
                        <tr>
                            <th>Учень</th>
                            <th>Предмет</th>
                            <th>Оцінка</th>
                            <th>Дата</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($grades as $grade):
                            $student_id = get_field('student', $grade->ID);
                            $student = get_post($student_id);
                            ?>
                            <tr>
                                <td><?php echo esc_html($student->post_title); ?></td>
                                <td><?php echo esc_html(get_field('subject', $grade->ID)); ?></td>
                                <td><?php echo esc_html(get_field('value', $grade->ID)); ?></td>
                                <td><?php echo esc_html(get_field('date', $grade->ID)); ?></td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            <?php else: ?>
                <p>Наразі немає доступних оцінок.</p>
            <?php endif; ?>
        </div>
        <?php
        return ob_get_clean();
    }
}

// Ініціалізація плагіну
function init_electronic_journal() {
    // Перевірка наявності залежностей
    if (!class_exists('ACF') || !class_exists('PhpOffice\PhpSpreadsheet\IOFactory')) {
        add_action('admin_notices', function() {
            echo '<div class="notice notice-error"><p>Для роботи плагіну "Електронний Журнал" необхідно встановити та активувати ACF Pro та PhpSpreadsheet.</p></div>';
        });
        return;
    }

    // Створення об'єкта плагіну
    new Electronic_Journal();
}

add_action('plugins_loaded', 'init_electronic_journal');
