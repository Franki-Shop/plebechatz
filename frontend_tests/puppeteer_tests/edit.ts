import type {Page} from "puppeteer";

import common from "../puppeteer_lib/common";

async function trigger_edit_last_message(page: Page): Promise<void> {
    await page.evaluate(() => {
        const $msg = $("#zhome .message_row").last();
        $msg.find(".message_control_button.actions_hover").trigger("click");
        $(".popover_edit_message").trigger("click");
    });
    await page.waitForSelector(".message_edit_content", {visible: true});
}

async function edit_stream_message(page: Page, topic: string, content: string): Promise<void> {
    await trigger_edit_last_message(page);

    await common.clear_and_type(page, ".message_edit_topic", topic);
    await common.clear_and_type(page, ".message_edit_content", content);
    await page.click(".message_edit_save");

    await common.wait_for_fully_processed_message(page, content);
}

async function test_stream_message_edit(page: Page): Promise<void> {
    await common.send_message(page, "stream", {
        stream: "Verona",
        topic: "edits",
        content: "test editing",
    });

    await edit_stream_message(page, "edited", "test edited");

    await common.check_messages_sent(page, "zhome", [["Verona > edited", ["test edited"]]]);
}

async function test_edit_message_with_slash_me(page: Page): Promise<void> {
    await common.send_message(page, "stream", {
        stream: "Verona",
        topic: "edits",
        content: "/me test editing a message with me",
    });
    await page.waitForFunction(
        () => $(".last_message .status-message").text() === "test editing a message with me",
    );
    await page.waitForFunction(
        () => $(".last_message .sender_name-in-status").text().trim() === "Desdemona",
    );

    await edit_stream_message(page, "edited", "/me test edited a message with me");

    await page.waitForFunction(
        () => $(".last_message .status-message").text() === "test edited a message with me",
    );
    await page.waitForFunction(
        () => $(".last_message .sender_name-in-status").text().trim() === "Desdemona",
    );
}

async function test_edit_private_message(page: Page): Promise<void> {
    await common.send_message(page, "private", {
        recipient: "cordelia@zulip.com",
        content: "test editing pm",
    });
    await trigger_edit_last_message(page);

    await common.clear_and_type(page, ".message_edit_content", "test edited pm");
    await page.click(".message_edit_save");
    await common.wait_for_fully_processed_message(page, "test edited pm");

    await common.check_messages_sent(page, "zhome", [
        ["You and Cordelia, Lear's daughter", ["test edited pm"]],
    ]);
}

async function edit_tests(page: Page): Promise<void> {
    await common.log_in(page);
    await page.click(".top_left_all_messages");
    await page.waitForSelector("#zhome .message_row", {visible: true});

    await test_stream_message_edit(page);
    await test_edit_message_with_slash_me(page);
    await test_edit_private_message(page);
}

common.run_test(edit_tests);
